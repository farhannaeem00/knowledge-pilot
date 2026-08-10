"""
Highlight endpoints - version-scoped CRUD.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.exceptions import NotFoundError
from app.infrastructure.db.models.user import User
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.highlight_repository import HighlightRepository
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository
from app.presentation.api.v1.schemas.highlight import HighlightCreate, HighlightOut
from app.presentation.dependencies import (
    get_current_user,
    get_document_repository,
    get_highlight_repository,
    get_workspace_repository,
)

router = APIRouter(
    prefix="/workspaces/{workspace_id}/documents/{document_id}/highlights", tags=["highlights"]
)


async def _verify_and_get_version(
    *, owner_id: UUID, workspace_id: UUID, document_id: UUID, workspace_repo, document_repo
):
    workspace = await workspace_repo.get_by_id(workspace_id)
    if not workspace or workspace.owner_id != owner_id or workspace.status == "trashed":
        raise NotFoundError("Workspace not found")
    document = await document_repo.get_document_by_id(document_id)
    if not document or document.workspace_id != workspace_id:
        raise NotFoundError("Document not found")
    version = await document_repo.get_current_version(document_id)
    if not version:
        raise NotFoundError("Document has no processed version yet")
    return version


@router.post("", response_model=HighlightOut, status_code=status.HTTP_201_CREATED)
async def create_highlight(
    workspace_id: UUID,
    document_id: UUID,
    payload: HighlightCreate,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    highlight_repo: HighlightRepository = Depends(get_highlight_repository),
) -> HighlightOut:
    version = await _verify_and_get_version(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    highlight = await highlight_repo.create(
        version_id=version.id,
        level=payload.level,
        start_offset=payload.start_offset,
        end_offset=payload.end_offset,
        highlighted_text=payload.highlighted_text,
        note=payload.note,
    )
    return HighlightOut.model_validate(highlight)


@router.get("", response_model=list[HighlightOut])
async def list_highlights(
    workspace_id: UUID,
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    highlight_repo: HighlightRepository = Depends(get_highlight_repository),
) -> list[HighlightOut]:
    version = await _verify_and_get_version(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    highlights = await highlight_repo.list_by_version(version.id)
    return [HighlightOut.model_validate(h) for h in highlights]


@router.delete("/{highlight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_highlight(
    workspace_id: UUID,
    document_id: UUID,
    highlight_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    highlight_repo: HighlightRepository = Depends(get_highlight_repository),
) -> None:
    version = await _verify_and_get_version(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    highlight = await highlight_repo.get_by_id(highlight_id)
    if not highlight or highlight.version_id != version.id:
        raise NotFoundError("Highlight not found")
    await highlight_repo.delete(highlight)