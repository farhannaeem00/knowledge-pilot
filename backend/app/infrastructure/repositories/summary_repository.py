"""
Summary persistence - sync variant for the Celery task, async variant
for API reads (same split pattern as document_chunk_repository.py).
"""
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.infrastructure.db.models.summary import Summary


class SyncSummaryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_pending(self, *, version_id: UUID, style: str) -> Summary:
        # Deactivate any prior active summary of the same style for this version.
        self.session.execute(
            update(Summary)
            .where(Summary.version_id == version_id, Summary.style == style, Summary.is_active.is_(True))
            .values(is_active=False)
        )
        summary = Summary(version_id=version_id, style=style, status="pending", is_active=True)
        self.session.add(summary)
        self.session.commit()
        self.session.refresh(summary)
        return summary

    def mark_processing(self, summary: Summary) -> None:
        summary.status = "processing"
        self.session.commit()

    def mark_done(self, summary: Summary, *, content_json: dict, model_used: str) -> None:
        summary.status = "done"
        summary.content_json = content_json
        summary.model_used = model_used
        summary.error_message = None
        self.session.commit()

    def mark_failed(self, summary: Summary, *, error_message: str) -> None:
        summary.status = "failed"
        summary.error_message = error_message[:1000]
        self.session.commit()


class SummaryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active(self, *, version_id: UUID, style: str) -> Summary | None:
        result = await self.session.execute(
            select(Summary).where(
                Summary.version_id == version_id, Summary.style == style, Summary.is_active.is_(True)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, summary_id: UUID) -> Summary | None:
        result = await self.session.execute(select(Summary).where(Summary.id == summary_id))
        return result.scalar_one_or_none()

    async def list_by_version(self, version_id: UUID) -> list[Summary]:
        result = await self.session.execute(
            select(Summary).where(Summary.version_id == version_id).order_by(Summary.created_at.desc())
        )
        return list(result.scalars().all())
