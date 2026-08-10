"""
DocumentChunk persistence. Two variants deliberately exist:

- SyncDocumentChunkRepository: used by the Celery worker (sync session).
- DocumentChunkRepository: async, used by API routes for read-only
  operations like chunk_count, keeping the API layer non-blocking.

Both wrap the same table; splitting by session flavor rather than
responsibility is a pragmatic call for this stage.
"""
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.infrastructure.db.models.document_chunk import DocumentChunk


class SyncDocumentChunkRepository:
    def __init__(self, session: Session):
        self.session = session

    def delete_by_version(self, version_id: UUID) -> None:
        self.session.execute(delete(DocumentChunk).where(DocumentChunk.version_id == version_id))
        self.session.commit()

    def bulk_create(self, *, version_id: UUID, chunks: list[str]) -> None:
        objects = [
            DocumentChunk(version_id=version_id, chunk_index=i, content=c, char_count=len(c))
            for i, c in enumerate(chunks)
        ]
        self.session.add_all(objects)
        self.session.commit()


class DocumentChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_by_version(self, version_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(DocumentChunk).where(DocumentChunk.version_id == version_id)
        )
        return result.scalar_one()

    async def list_by_version(self, version_id: UUID) -> list[DocumentChunk]:
        result = await self.session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.version_id == version_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(result.scalars().all())
