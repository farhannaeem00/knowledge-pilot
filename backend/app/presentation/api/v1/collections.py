"""
Collection endpoints - workspace-scoped CRUD + membership management.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.exceptions import NotFoundError
from app.infrastructure.db.models.user import User
from app.infrastructure.repositories.collection_repository import CollectionRepository
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository
from app.presentation.api.v1.schemas.collection import (
    AddDocumentToCollectionRequest,
    CollectionCreate,
    CollectionOut,
)
from app.presentation.api.v1.schemas.document import DocumentOut
from app.presentation.dependencies import get_collection_repository, get_current_user, get_workspace_repository

router = APIRouter(prefix="/workspaces/{workspace_id}/collections", tags=["collections"])


async def _verify_workspace(*, owner_id: UUID, workspace_id: UUID, workspace_repo: WorkspaceRepository):
    workspace = await workspace_repo.get_by_id(workspace_id)
    if not workspace or workspace.owner_id != owner_id or workspace.status == "trashed":
        raise NotFoundError("Workspace not found")
    return workspace


@router.post("", response_model=CollectionOut, status_code=status.HTTP_201_CREATED)
async def create_collection(
    workspace_id: UUID,
    payload: CollectionCreate,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    collection_repo: CollectionRepository = Depends(get_collection_repository),
) -> CollectionOut:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    collection = await collection_repo.create(workspace_id=workspace_id, name=payload.name)
    return CollectionOut.model_validate(collection)


@router.get("", response_model=list[CollectionOut])
async def list_collections(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    collection_repo: CollectionRepository = Depends(get_collection_repository),
) -> list[CollectionOut]:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    collections = await collection_repo.list_by_workspace(workspace_id)
    return [CollectionOut.model_validate(c) for c in collections]


@router.post("/{collection_id}/documents", status_code=status.HTTP_204_NO_CONTENT)
async def add_document_to_collection(
    workspace_id: UUID,
    collection_id: UUID,
    payload: AddDocumentToCollectionRequest,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    collection_repo: CollectionRepository = Depends(get_collection_repository),
) -> None:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    collection = await collection_repo.get_by_id(collection_id)
    if not collection or collection.workspace_id != workspace_id:
        raise NotFoundError("Collection not found")
    await collection_repo.add_document(collection_id=collection_id, document_id=payload.document_id)


@router.delete("/{collection_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document_from_collection(
    workspace_id: UUID,
    collection_id: UUID,
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    collection_repo: CollectionRepository = Depends(get_collection_repository),
) -> None:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    await collection_repo.remove_document(collection_id=collection_id, document_id=document_id)


@router.get("/{collection_id}/documents", response_model=list[DocumentOut])
async def list_collection_documents(
    workspace_id: UUID,
    collection_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    collection_repo: CollectionRepository = Depends(get_collection_repository),
) -> list[DocumentOut]:
    await _verify_workspace(owner_id=current_user.id, workspace_id=workspace_id, workspace_repo=workspace_repo)
    documents = await collection_repo.list_documents(collection_id)
    return [DocumentOut.model_validate(d) for d in documents]