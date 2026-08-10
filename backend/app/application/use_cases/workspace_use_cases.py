"""
Workspace use cases. Ownership is enforced here (not in the router) so
it's impossible to bypass by adding a new endpoint later.
"""
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.infrastructure.db.models.workspace import Workspace
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository


class CreateWorkspaceUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    async def execute(self, *, owner_id: UUID, name: str) -> Workspace:
        return await self.repo.create(owner_id=owner_id, name=name)


class ListWorkspacesUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    async def execute(self, *, owner_id: UUID) -> list[Workspace]:
        return await self.repo.list_by_owner(owner_id)


class GetWorkspaceUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    async def execute(self, *, owner_id: UUID, workspace_id: UUID) -> Workspace:
        workspace = await self.repo.get_by_id(workspace_id)
        if not workspace or workspace.owner_id != owner_id or workspace.status == "trashed":
            # Same error for "doesn't exist" and "not yours" - avoids
            # leaking which workspace IDs exist to unauthorized users.
            raise NotFoundError("Workspace not found")
        return workspace


class UpdateWorkspaceUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    async def execute(self, *, owner_id: UUID, workspace_id: UUID, name: str | None) -> Workspace:
        workspace = await GetWorkspaceUseCase(self.repo).execute(owner_id=owner_id, workspace_id=workspace_id)
        fields = {}
        if name is not None:
            fields["name"] = name
        return await self.repo.update(workspace, **fields)


class DeleteWorkspaceUseCase:
    def __init__(self, repo: WorkspaceRepository):
        self.repo = repo

    async def execute(self, *, owner_id: UUID, workspace_id: UUID) -> None:
        workspace = await GetWorkspaceUseCase(self.repo).execute(owner_id=owner_id, workspace_id=workspace_id)
        await self.repo.soft_delete(workspace)
