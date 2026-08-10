from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.folder import Folder


class FolderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, workspace_id: UUID, parent_id: UUID | None, name: str) -> Folder:
        folder = Folder(workspace_id=workspace_id, parent_id=parent_id, name=name)
        self.session.add(folder)
        await self.session.commit()
        await self.session.refresh(folder)
        return folder

    async def get_by_id(self, folder_id: UUID) -> Folder | None:
        result = await self.session.execute(select(Folder).where(Folder.id == folder_id))
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: UUID) -> list[Folder]:
        result = await self.session.execute(
            select(Folder).where(Folder.workspace_id == workspace_id).order_by(Folder.name)
        )
        return list(result.scalars().all())

    async def update(self, folder: Folder, **fields) -> Folder:
        for key, value in fields.items():
            if value is not None:
                setattr(folder, key, value)
        await self.session.commit()
        await self.session.refresh(folder)
        return folder

    async def delete(self, folder: Folder) -> None:
        await self.session.delete(folder)
        await self.session.commit() 