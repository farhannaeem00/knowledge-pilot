"""
Note persistence (async - pure CRUD, no background job needed).
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.note import Note


class NoteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        workspace_id: UUID,
        document_id: UUID | None,
        title: str,
        content_md: str,
        tags: list[str] | None,
    ) -> Note:
        note = Note(
            workspace_id=workspace_id,
            document_id=document_id,
            title=title,
            content_md=content_md,
            tags=tags or [],
        )
        self.session.add(note)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def get_by_id(self, note_id: UUID) -> Note | None:
        result = await self.session.execute(select(Note).where(Note.id == note_id))
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: UUID) -> list[Note]:
        result = await self.session.execute(
            select(Note)
            .where(Note.workspace_id == workspace_id)
            .order_by(Note.is_pinned.desc(), Note.updated_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, note: Note, **fields) -> Note:
        for key, value in fields.items():
            if value is not None:
                setattr(note, key, value)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def delete(self, note: Note) -> None:
        await self.session.delete(note)
        await self.session.commit()