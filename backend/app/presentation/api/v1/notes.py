"""
Note endpoints - workspace-scoped CRUD.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.exceptions import NotFoundError
from app.infrastructure.db.models.user import User
from app.infrastructure.repositories.note_repository import NoteRepository
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository
from app.presentation.api.v1.schemas.note import NoteCreate, NoteOut, NoteUpdate
from app.presentation.dependencies import get_current_user, get_note_repository, get_workspace_repository

router = APIRouter(prefix="/workspaces/{workspace_id}/notes", tags=["notes"])


async def _verify_workspace(*, owner_id: UUID, workspace_id: UUID, workspace_repo: WorkspaceRepository):
    workspace = await workspace_repo.get_by_id(workspace_id)
    if not workspace or workspace.owner_id != owner_id or workspace.status == "trashed":
        raise NotFoundError("Workspace not found")
    return workspace


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
async def create_note(
    workspace_id: UUID,
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    note_repo: NoteRepository = Depends(get_note_repository),
) -> NoteOut:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    note = await note_repo.create(
        workspace_id=workspace_id,
        document_id=payload.document_id,
        title=payload.title,
        content_md=payload.content_md,
        tags=payload.tags,
    )
    return NoteOut.model_validate(note)


@router.get("", response_model=list[NoteOut])
async def list_notes(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    note_repo: NoteRepository = Depends(get_note_repository),
) -> list[NoteOut]:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    notes = await note_repo.list_by_workspace(workspace_id)
    return [NoteOut.model_validate(n) for n in notes]


@router.patch("/{note_id}", response_model=NoteOut)
async def update_note(
    workspace_id: UUID,
    note_id: UUID,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    note_repo: NoteRepository = Depends(get_note_repository),
) -> NoteOut:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    note = await note_repo.get_by_id(note_id)
    if not note or note.workspace_id != workspace_id:
        raise NotFoundError("Note not found")
    updated = await note_repo.update(
        note,
        title=payload.title,
        content_md=payload.content_md,
        tags=payload.tags,
        is_pinned=payload.is_pinned,
    )
    return NoteOut.model_validate(updated)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    workspace_id: UUID,
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    note_repo: NoteRepository = Depends(get_note_repository),
) -> None:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    note = await note_repo.get_by_id(note_id)
    if not note or note.workspace_id != workspace_id:
        raise NotFoundError("Note not found")
    await note_repo.delete(note)