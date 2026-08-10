"""
Celery task: generate a structured summary for a document version via Groq.

Uses the sync OpenAI-compatible client directly (pointed at Groq) rather
than the async GroqProvider used elsewhere - this task runs in the sync
Celery worker context, consistent with document_processing_tasks.py.
"""
import time
import json
import logging
from uuid import UUID as UUIDType

from openai import OpenAI
from sqlalchemy import select

from app.infrastructure.db.models.workspace import Workspace
from app.core.config import settings
from app.infrastructure.celery_app import celery_app
from app.infrastructure.db.models.document import Document
from app.infrastructure.db.models.document_chunk import DocumentChunk
from app.infrastructure.db.models.document_version import DocumentVersion
from app.infrastructure.db.models.summary import Summary
from app.infrastructure.db.sync_session import SyncSessionLocal
from app.infrastructure.prompts.summary_prompts import build_system_prompt, build_user_prompt
from app.infrastructure.repositories.notification_repository import SyncNotificationRepository
from app.infrastructure.repositories.summary_repository import SyncSummaryRepository
from app.infrastructure.repositories.ai_usage_repository import SyncAIUsageRepository

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_INPUT_CHARS = 12000  # keeps us comfortably within context; RAG (Step 7) handles longer docs differently


@celery_app.task(name="generate_summary", bind=True, max_retries=2)
def generate_summary(self, summary_id: str) -> None:
    session = SyncSessionLocal()
    summary_uuid = UUIDType(summary_id)
    try:
        summary = session.get(Summary, summary_uuid)
        if not summary:
            logger.error("Summary %s not found", summary_id)
            return

        version = session.get(DocumentVersion, summary.version_id)
        if not version:
            logger.error("DocumentVersion %s not found for summary %s", summary.version_id, summary_id)
            return
        document = session.get(Document, version.document_id)

        summary_repo = SyncSummaryRepository(session)
        summary_repo.mark_processing(summary)

        chunk_rows = session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.version_id == version.id)
            .order_by(DocumentChunk.chunk_index)
        ).scalars().all()

        if not chunk_rows:
            summary_repo.mark_failed(summary, error_message="No processed content available to summarize")
            return

        content_text = "\n\n".join(c.content for c in chunk_rows)[:MAX_INPUT_CHARS]

        start_time = time.monotonic()
        client = OpenAI(api_key=settings.GROQ_API_KEY, base_url=GROQ_BASE_URL)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": build_system_prompt(summary.style)},
                {
                    "role": "user",
                    "content": build_user_prompt(
                        title=document.title if document else "Untitled", content=content_text
                    ),
                },
            ],
            max_tokens=2048,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content or "{}"

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            summary_repo.mark_failed(summary, error_message=f"Model returned invalid JSON: {exc}")
            return

        latency_ms = int((time.monotonic() - start_time) * 1000)
        summary_repo.mark_done(summary, content_json=parsed, model_used=GROQ_MODEL)

        workspace = session.get(Workspace, document.workspace_id) if document else None
        if workspace:
            SyncAIUsageRepository(session).log(
                user_id=workspace.owner_id,
                workspace_id=workspace.id,
                feature="summary",
                provider="groq",
                model=GROQ_MODEL,
                tokens_in=response.usage.prompt_tokens if response.usage else None,
                tokens_out=response.usage.completion_tokens if response.usage else None,
                latency_ms=latency_ms,
            )
            SyncNotificationRepository(session).create(
                user_id=workspace.owner_id,
                type_="summary_ready",
                payload={"summary_id": str(summary.id), "style": summary.style, "document_title": document.title},
            )

        

        workspace = session.get(Workspace, document.workspace_id) if document else None
        if workspace:
            SyncNotificationRepository(session).create(
                user_id=workspace.owner_id,
                type_="summary_ready",
                payload={"summary_id": str(summary.id), "style": summary.style, "document_title": document.title},
            )

    except Exception as exc:
        session.rollback()
        summary = session.get(Summary, summary_uuid)
        if summary:
            SyncSummaryRepository(session).mark_failed(summary, error_message=str(exc))
        logger.exception("Summary generation failed for %s", summary_id)
        raise self.retry(exc=exc, countdown=15) from exc
    finally:
        session.close()
