"""
Folder endpoints - workspace-scoped CRUD.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.exceptions import NotFoundError
from app.infrastructure.db.models.user import User
from app.infrastructure.repositories.folder_repository import FolderRepository
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository
from app.presentation.api.v1.schemas.folder import FolderCreate, FolderOut, FolderUpdate
from app.presentation.dependencies import get_current_user, get_folder_repository, get_workspace_repository

router = APIRouter(prefix="/workspaces/{workspace_id}/folders", tags=["folders"])


async def _verify_workspace(*, owner_id: UUID, workspace_id: UUID, workspace_repo: WorkspaceRepository):
    workspace = await workspace_repo.get_by_id(workspace_id)
    if not workspace or workspace.owner_id != owner_id or workspace.status == "trashed":
        raise NotFoundError("Workspace not found")
    return workspace


@router.post("", response_model=FolderOut, status_code=status.HTTP_201_CREATED)
async def create_folder(
    workspace_id: UUID,
    payload: FolderCreate,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    folder_repo: FolderRepository = Depends(get_folder_repository),
) -> FolderOut:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    folder = await folder_repo.create(workspace_id=workspace_id, parent_id=payload.parent_id, name=payload.name)
    return FolderOut.model_validate(folder)


@router.get("", response_model=list[FolderOut])
async def list_folders(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    folder_repo: FolderRepository = Depends(get_folder_repository),
) -> list[FolderOut]:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    folders = await folder_repo.list_by_workspace(workspace_id)
    return [FolderOut.model_validate(f) for f in folders]


@router.patch("/{folder_id}", response_model=FolderOut)
async def update_folder(
    workspace_id: UUID,
    folder_id: UUID,
    payload: FolderUpdate,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    folder_repo: FolderRepository = Depends(get_folder_repository),
) -> FolderOut:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    folder = await folder_repo.get_by_id(folder_id)
    if not folder or folder.workspace_id != workspace_id:
        raise NotFoundError("Folder not found")
    updated = await folder_repo.update(folder, name=payload.name, parent_id=payload.parent_id)
    return FolderOut.model_validate(updated)


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    workspace_id: UUID,
    folder_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    folder_repo: FolderRepository = Depends(get_folder_repository),
) -> None:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    folder = await folder_repo.get_by_id(folder_id)
    if not folder or folder.workspace_id != workspace_id:
        raise NotFoundError("Folder not found")
    await folder_repo.delete(folder)