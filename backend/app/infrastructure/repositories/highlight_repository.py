"""
Highlight persistence (async - pure CRUD).
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.highlight import Highlight


class HighlightRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        version_id: UUID,
        level: str,
        start_offset: int,
        end_offset: int,
        highlighted_text: str,
        note: str | None,
    ) -> Highlight:
        highlight = Highlight(
            version_id=version_id,
            level=level,
            start_offset=start_offset,
            end_offset=end_offset,
            highlighted_text=highlighted_text,
            note=note,
        )
        self.session.add(highlight)
        await self.session.commit()
        await self.session.refresh(highlight)
        return highlight

    async def get_by_id(self, highlight_id: UUID) -> Highlight | None:
        result = await self.session.execute(select(Highlight).where(Highlight.id == highlight_id))
        return result.scalar_one_or_none()

    async def list_by_version(self, version_id: UUID) -> list[Highlight]:
        result = await self.session.execute(
            select(Highlight).where(Highlight.version_id == version_id).order_by(Highlight.start_offset)
        )
        return list(result.scalars().all())

    async def delete(self, highlight: Highlight) -> None:
        await self.session.delete(highlight)
        await self.session.commit()