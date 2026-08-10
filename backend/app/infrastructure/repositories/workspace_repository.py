"""
Concrete Postgres implementation for Workspace persistence.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.workspace import Workspace


class WorkspaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, owner_id: UUID, name: str) -> Workspace:
        workspace = Workspace(owner_id=owner_id, name=name)
        self.session.add(workspace)
        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def get_by_id(self, workspace_id: UUID) -> Workspace | None:
        result = await self.session.execute(select(Workspace).where(Workspace.id == workspace_id))
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_id: UUID, *, include_trashed: bool = False) -> list[Workspace]:
        query = select(Workspace).where(Workspace.owner_id == owner_id)
        if not include_trashed:
            query = query.where(Workspace.status != "trashed")
        result = await self.session.execute(query.order_by(Workspace.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, workspace: Workspace, **fields) -> Workspace:
        for key, value in fields.items():
            setattr(workspace, key, value)
        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def soft_delete(self, workspace: Workspace) -> Workspace:
        workspace.status = "trashed"
        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace
