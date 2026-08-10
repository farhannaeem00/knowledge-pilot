"""
Workspace + Document endpoints.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from app.presentation.api.v1.schemas.document import DocumentUpdate

from app.application.use_cases.document_use_cases import (
    AddDocumentVersionUseCase,
    CreateDocumentFromPasteUseCase,
    CreateDocumentFromUploadUseCase,
    CreateDocumentFromUrlUseCase,
    GetDocumentUseCase,
    ListDocumentsUseCase,
)
from app.application.use_cases.workspace_use_cases import (
    CreateWorkspaceUseCase,
    DeleteWorkspaceUseCase,
    GetWorkspaceUseCase,
    ListWorkspacesUseCase,
    UpdateWorkspaceUseCase,
)
from app.infrastructure.db.models.user import User
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository
from app.infrastructure.storage.local_storage import LocalStorage
from app.presentation.api.v1.schemas.document import (
    DocumentCreateFromPaste,
    DocumentCreateFromUrl,
    DocumentOut,
    DocumentVersionOut,
    DocumentWithVersionsOut,
)
from app.presentation.api.v1.schemas.workspace import WorkspaceCreate, WorkspaceOut, WorkspaceUpdate
from app.presentation.dependencies import (
    get_current_user,
    get_document_chunk_repository,
    get_document_repository,
    get_storage,
    get_workspace_repository,
)
from app.infrastructure.repositories.document_chunk_repository import DocumentChunkRepository

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> WorkspaceOut:
    workspace = await CreateWorkspaceUseCase(repo).execute(owner_id=current_user.id, name=payload.name)
    return WorkspaceOut.model_validate(workspace)


@router.get("", response_model=list[WorkspaceOut])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> list[WorkspaceOut]:
    workspaces = await ListWorkspacesUseCase(repo).execute(owner_id=current_user.id)
    return [WorkspaceOut.model_validate(w) for w in workspaces]


@router.get("/{workspace_id}", response_model=WorkspaceOut)
async def get_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> WorkspaceOut:
    workspace = await GetWorkspaceUseCase(repo).execute(owner_id=current_user.id, workspace_id=workspace_id)
    return WorkspaceOut.model_validate(workspace)


@router.patch("/{workspace_id}", response_model=WorkspaceOut)
async def update_workspace(
    workspace_id: UUID,
    payload: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> WorkspaceOut:
    workspace = await UpdateWorkspaceUseCase(repo).execute(
        owner_id=current_user.id, workspace_id=workspace_id, name=payload.name
    )
    return WorkspaceOut.model_validate(workspace)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> None:
    await DeleteWorkspaceUseCase(repo).execute(owner_id=current_user.id, workspace_id=workspace_id)


# --- Documents ---


@router.post("/{workspace_id}/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    workspace_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    storage: LocalStorage = Depends(get_storage),
) -> DocumentOut:
    content = await file.read()
    document, _ = await CreateDocumentFromUploadUseCase(workspace_repo, document_repo, storage).execute(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        filename=file.filename or "upload",
        content_type=file.content_type,
        content=content,
    )
    return DocumentOut.model_validate(document)


@router.post(
    "/{workspace_id}/documents/{document_id}/versions",
    response_model=DocumentVersionOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_new_version(
    workspace_id: UUID,
    document_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    storage: LocalStorage = Depends(get_storage),
) -> DocumentVersionOut:
    content = await file.read()
    version = await AddDocumentVersionUseCase(workspace_repo, document_repo, storage).execute(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        filename=file.filename or "upload",
        content_type=file.content_type,
        content=content,
    )
    return DocumentVersionOut.model_validate(version)


@router.post("/{workspace_id}/documents/url", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def add_document_from_url(
    workspace_id: UUID,
    payload: DocumentCreateFromUrl,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    storage: LocalStorage = Depends(get_storage),
) -> DocumentOut:
    document, _ = await CreateDocumentFromUrlUseCase(workspace_repo, document_repo, storage).execute(
        owner_id=current_user.id, workspace_id=workspace_id, url=payload.url
    )
    return DocumentOut.model_validate(document)


@router.post("/{workspace_id}/documents/paste", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def add_document_from_paste(
    workspace_id: UUID,
    payload: DocumentCreateFromPaste,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    storage: LocalStorage = Depends(get_storage),
) -> DocumentOut:
    document, _ = await CreateDocumentFromPasteUseCase(workspace_repo, document_repo, storage).execute(
        owner_id=current_user.id, workspace_id=workspace_id, title=payload.title, content_text=payload.content
    )
    return DocumentOut.model_validate(document)


@router.get("/{workspace_id}/documents", response_model=list[DocumentOut])
async def list_documents(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
) -> list[DocumentOut]:
    documents = await ListDocumentsUseCase(workspace_repo, document_repo).execute(
        owner_id=current_user.id, workspace_id=workspace_id
    )
    return [DocumentOut.model_validate(d) for d in documents]


@router.get("/{workspace_id}/documents/{document_id}", response_model=DocumentWithVersionsOut)
async def get_document(
    workspace_id: UUID,
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    chunk_repo: DocumentChunkRepository = Depends(get_document_chunk_repository),
) -> DocumentWithVersionsOut:
    document, versions = await GetDocumentUseCase(workspace_repo, document_repo).execute(
        owner_id=current_user.id, workspace_id=workspace_id, document_id=document_id
    )
    version_outs = []
    for v in versions:
        count = await chunk_repo.count_by_version(v.id)
        version_out = DocumentVersionOut.model_validate(v)
        version_out.chunk_count = count
        version_outs.append(version_out)

    return DocumentWithVersionsOut(
        **DocumentOut.model_validate(document).model_dump(),
        versions=version_outs,
    )

@router.patch("/{workspace_id}/documents/{document_id}", response_model=DocumentOut)
async def update_document(
    workspace_id: UUID,
    document_id: UUID,
    payload: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
) -> DocumentOut:
    from app.application.use_cases.workspace_use_cases import GetWorkspaceUseCase
    from app.core.exceptions import NotFoundError

    await GetWorkspaceUseCase(workspace_repo).execute(owner_id=current_user.id, workspace_id=workspace_id)
    document = await document_repo.get_document_by_id(document_id)
    if not document or document.workspace_id != workspace_id:
        raise NotFoundError("Document not found")

    updated = await document_repo.update(
        document,
        title=payload.title,
        folder_id=payload.folder_id,
        tags=payload.tags,
        is_favorite=payload.is_favorite,
        status=payload.status,
    )
    return DocumentOut.model_validate(updated)