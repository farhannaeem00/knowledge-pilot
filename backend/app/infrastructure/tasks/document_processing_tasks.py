"""
Celery task: parse -> clean -> chunk -> embed a document version.

Idempotent by design: re-running this task for the same version_id
deletes any existing chunks/embeddings for that version before inserting
new ones, so Celery's at-least-once delivery (retries) never produces
duplicates.
"""
import logging
from uuid import UUID as UUIDType

from app.infrastructure.celery_app import celery_app
from app.infrastructure.db.models.document import Document
from app.infrastructure.db.models.document_version import DocumentVersion
from app.infrastructure.db.sync_session import SyncSessionLocal
from app.infrastructure.embeddings.local_embedder import embed_texts
from app.infrastructure.parsing.chunker import chunk_text
from app.infrastructure.parsing.text_extractor import extract_text
from app.infrastructure.repositories.document_chunk_repository import SyncDocumentChunkRepository
from app.infrastructure.repositories.embedding_repository import SyncEmbeddingRepository
from app.infrastructure.storage.local_storage import LocalStorage
    
from app.infrastructure.repositories.notification_repository import SyncNotificationRepository

logger = logging.getLogger(__name__)


@celery_app.task(name="process_document_version", bind=True, max_retries=2)
def process_document_version(self, version_id: str) -> None:
    session = SyncSessionLocal()
    version_uuid = UUIDType(version_id)
    try:
        version = session.get(DocumentVersion, version_uuid)
        if not version:
            logger.error("DocumentVersion %s not found", version_id)
            return

        document = session.get(Document, version.document_id)
        if not document:
            logger.error("Document %s not found for version %s", version.document_id, version_id)
            return

        version.status = "processing"
        session.commit()

        storage = LocalStorage()
        content = storage.read(key=version.storage_key)

        result = extract_text(content=content, source_type=document.source_type)
        chunks = chunk_text(result.text)

        chunk_repo = SyncDocumentChunkRepository(session)
        chunk_repo.delete_by_version(version.id)
        chunk_repo.bulk_create(version_id=version.id, chunks=chunks)

        if not chunks:
            version.status = "failed" if not result.is_partial else "failed_partial"
            version.error_message = (
                "No extractable text content found"
                if not result.is_partial
                else f"Failed to extract {len(result.failed_pages)} page(s)"
            )
            session.commit()
            return

        # Fetch the freshly-created chunks (with real IDs) to embed against.
        from sqlalchemy import select

        from app.infrastructure.db.models.document_chunk import DocumentChunk

        chunk_rows = session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.version_id == version.id)
            .order_by(DocumentChunk.chunk_index)
        ).scalars().all()

        vectors = embed_texts([c.content for c in chunk_rows])

        embedding_repo = SyncEmbeddingRepository(session)
        embedding_repo.delete_by_chunk_ids([c.id for c in chunk_rows])
        embedding_repo.bulk_create(
            chunk_ids=[c.id for c in chunk_rows], vectors=vectors, model="BAAI/bge-base-en-v1.5"
        )

        if result.is_partial:
            version.status = "failed_partial"
            version.error_message = f"Failed to extract {len(result.failed_pages)} page(s): {result.failed_pages}"
        else:
            version.status = "done"
            version.error_message = None

        session.commit()

        # Fire a notification for the document's workspace owner.
        from app.infrastructure.db.models.workspace import Workspace

        workspace = session.get(Workspace, document.workspace_id)
        if workspace:
            notif_repo = SyncNotificationRepository(session)
            notif_repo.create(
                user_id=workspace.owner_id,
                type_="processing_complete" if version.status == "done" else "processing_failed",
                payload={
                    "document_id": str(document.id),
                    "document_title": document.title,
                    "version_id": str(version.id),
                    "status": version.status,
                },
            )

    except Exception as exc:
        session.rollback()
        version = session.get(DocumentVersion, version_uuid)
        if version:
            version.status = "failed"
            version.error_message = str(exc)[:1000]
            session.commit()

            document = session.get(Document, version.document_id)
            if document:
                from app.infrastructure.db.models.workspace import Workspace

                workspace = session.get(Workspace, document.workspace_id)
                if workspace:
                    SyncNotificationRepository(session).create(
                        user_id=workspace.owner_id,
                        type_="processing_failed",
                        payload={"document_id": str(document.id), "error": str(exc)[:500]},
                    )
        logger.exception("Processing failed for version %s", version_id)
        raise self.retry(exc=exc, countdown=10) from exc
    finally:
        session.close()