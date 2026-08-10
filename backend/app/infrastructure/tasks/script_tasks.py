"""
Celery task: generate a platform-specific script via Groq.

Prefers the active "detailed" summary as source material if one exists
(tighter output), falls back to raw chunk content otherwise - a script
doesn't strictly require a summary to exist first.
"""
import json
import logging
import time
from uuid import UUID as UUIDType

from openai import OpenAI
from sqlalchemy import select

from app.core.config import settings
from app.infrastructure.celery_app import celery_app
from app.infrastructure.db.models.document import Document
from app.infrastructure.db.models.document_chunk import DocumentChunk
from app.infrastructure.db.models.script import Script
from app.infrastructure.db.models.summary import Summary
from app.infrastructure.db.sync_session import SyncSessionLocal
from app.infrastructure.prompts.script_prompts import build_system_prompt, build_user_prompt
from app.infrastructure.repositories.notification_repository import SyncNotificationRepository
from app.infrastructure.repositories.script_repository import SyncScriptRepository
from app.infrastructure.repositories.ai_usage_repository import SyncAIUsageRepository
from app.infrastructure.db.models.workspace import Workspace
logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_INPUT_CHARS = 10000


@celery_app.task(name="generate_script", bind=True, max_retries=2)
def generate_script(self, script_id: str) -> None:
    session = SyncSessionLocal()
    script_uuid = UUIDType(script_id)
    try:
        script = session.get(Script, script_uuid)
        if not script:
            logger.error("Script %s not found", script_id)
            return

        document = session.get(Document, script.document_id)
        script_repo = SyncScriptRepository(session)
        script_repo.mark_processing(script)

        # Prefer an existing "detailed" summary as source material.
        active_summary = session.execute(
            select(Summary).where(
                Summary.style == "detailed", Summary.status == "done", Summary.is_active.is_(True)
            )
        ).scalars().first()

        source_content = None
        if active_summary and active_summary.content_json:
            source_content = json.dumps(active_summary.content_json)
        else:
            # Fall back to raw chunks from the document's current version.
            from app.infrastructure.db.models.document_version import DocumentVersion

            version = session.execute(
                select(DocumentVersion).where(
                    DocumentVersion.document_id == script.document_id, DocumentVersion.is_current.is_(True)
                )
            ).scalar_one_or_none()
            if version:
                chunk_rows = session.execute(
                    select(DocumentChunk)
                    .where(DocumentChunk.version_id == version.id)
                    .order_by(DocumentChunk.chunk_index)
                ).scalars().all()
                source_content = "\n\n".join(c.content for c in chunk_rows)

        if not source_content:
            script_repo.mark_failed(script, error_message="No processed content available to generate a script from")
            return

        source_content = source_content[:MAX_INPUT_CHARS]
        start_time = time.monotonic()
        client = OpenAI(api_key=settings.GROQ_API_KEY, base_url=GROQ_BASE_URL)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": build_system_prompt(script.platform)},
                {
                    "role": "user",
                    "content": build_user_prompt(
                        title=document.title if document else "Untitled", source_content=source_content
                    ),
                },
            ],
            max_tokens=2048,
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content or "{}"

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            script_repo.mark_failed(script, error_message=f"Model returned invalid JSON: {exc}")
            return

        latency_ms = int((time.monotonic() - start_time) * 1000)
        script_repo.mark_done(script, content_json=parsed, model_used=GROQ_MODEL)


        workspace = session.get(Workspace, script.workspace_id)
        if workspace:
            SyncAIUsageRepository(session).log(
                user_id=workspace.owner_id,
                workspace_id=workspace.id,
                feature="script",
                provider="groq",
                model=GROQ_MODEL,
                tokens_in=response.usage.prompt_tokens if response.usage else None,
                tokens_out=response.usage.completion_tokens if response.usage else None,
                latency_ms=latency_ms,
            )
            SyncNotificationRepository(session).create(
                user_id=workspace.owner_id,
                type_="script_ready",
                payload={"script_id": str(script.id), "platform": script.platform},
            )

        

        workspace = session.get(Workspace, script.workspace_id)
        if workspace:
            SyncNotificationRepository(session).create(
                user_id=workspace.owner_id,
                type_="script_ready",
                payload={"script_id": str(script.id), "platform": script.platform},
            )
    except Exception as exc:
        session.rollback()
        script = session.get(Script, script_uuid)
        if script:
            SyncScriptRepository(session).mark_failed(script, error_message=str(exc))
        logger.exception("Script generation failed for %s", script_id)
        raise self.retry(exc=exc, countdown=15) from exc
    finally:
        session.close()