"""
Document use cases: create (upload/url/paste), add new version, list, get.
File validation (size, extension) happens here, not in the router, so it
applies consistently regardless of entry point.
"""
from uuid import UUID

import httpx
from app.infrastructure.tasks.document_processing_tasks import process_document_version
from app.application.interfaces.storage import StorageInterface
from app.application.use_cases.workspace_use_cases import GetWorkspaceUseCase
from app.core.config import settings
from app.core.exceptions import ValidationAppError
from app.infrastructure.db.models.document import Document
from app.infrastructure.db.models.document_version import DocumentVersion
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository
from app.infrastructure.storage.local_storage import generate_storage_key

MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def _validate_upload(filename: str, size_bytes: int) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise ValidationAppError(
            f"Unsupported file type '.{ext}'. Allowed: {', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)}"
        )
    if size_bytes > MAX_UPLOAD_BYTES:
        raise ValidationAppError(f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit")
    return ext


class CreateDocumentFromUploadUseCase:
    def __init__(
        self,
        workspace_repo: WorkspaceRepository,
        document_repo: DocumentRepository,
        storage: StorageInterface,
    ):
        self.workspace_repo = workspace_repo
        self.document_repo = document_repo
        self.storage = storage

    async def execute(
        self, *, owner_id: UUID, workspace_id: UUID, filename: str, content_type: str | None, content: bytes
    ) -> tuple[Document, DocumentVersion]:
        await GetWorkspaceUseCase(self.workspace_repo).execute(owner_id=owner_id, workspace_id=workspace_id)
        ext = _validate_upload(filename, len(content))

        document = await self.document_repo.create_document(
            workspace_id=workspace_id, title=filename, source_type=ext
        )
        storage_key = generate_storage_key(
            workspace_id=str(workspace_id), document_id=str(document.id), filename=filename
        )
        self.storage.save(key=storage_key, content=content)

        version = await self.document_repo.create_version(
            document_id=document.id,
            version_number=1,
            storage_key=storage_key,
            original_filename=filename,
            content_type=content_type,
            size_bytes=len(content),
        )
        version = await self.document_repo.create_version(
            document_id=document.id,
            version_number=1,
            storage_key=storage_key,
            original_filename=filename,
            content_type=content_type,
            size_bytes=len(content),
        )
        process_document_version.delay(str(version.id))
        return document, version


class AddDocumentVersionUseCase:
    """Re-uploading to an existing Document creates a new version, never overwrites."""

    def __init__(
        self,
        workspace_repo: WorkspaceRepository,
        document_repo: DocumentRepository,
        storage: StorageInterface,
    ):
        self.workspace_repo = workspace_repo
        self.document_repo = document_repo
        self.storage = storage

    async def execute(
        self,
        *,
        owner_id: UUID,
        workspace_id: UUID,
        document_id: UUID,
        filename: str,
        content_type: str | None,
        content: bytes,
    ) -> DocumentVersion:
        await GetWorkspaceUseCase(self.workspace_repo).execute(owner_id=owner_id, workspace_id=workspace_id)
        document = await self.document_repo.get_document_by_id(document_id)
        if not document or document.workspace_id != workspace_id:
            from app.core.exceptions import NotFoundError

            raise NotFoundError("Document not found")

        _validate_upload(filename, len(content))
        storage_key = generate_storage_key(
            workspace_id=str(workspace_id), document_id=str(document_id), filename=filename
        )
        self.storage.save(key=storage_key, content=content)

        next_version = await self.document_repo.get_next_version_number(document_id)
        version = await self.document_repo.create_version(
            document_id=document_id,
            version_number=next_version,
            storage_key=storage_key,
            original_filename=filename,
            content_type=content_type,
            size_bytes=len(content),
        )
        process_document_version.delay(str(version.id))
        return version
       


class CreateDocumentFromPasteUseCase:
    def __init__(
        self,
        workspace_repo: WorkspaceRepository,
        document_repo: DocumentRepository,
        storage: StorageInterface,
    ):
        self.workspace_repo = workspace_repo
        self.document_repo = document_repo
        self.storage = storage

    async def execute(
        self, *, owner_id: UUID, workspace_id: UUID, title: str, content_text: str
    ) -> tuple[Document, DocumentVersion]:
        await GetWorkspaceUseCase(self.workspace_repo).execute(owner_id=owner_id, workspace_id=workspace_id)
        content_bytes = content_text.encode("utf-8")

        document = await self.document_repo.create_document(
            workspace_id=workspace_id, title=title, source_type="paste"
        )
        storage_key = generate_storage_key(
            workspace_id=str(workspace_id), document_id=str(document.id), filename=f"{title}.txt"
        )
        self.storage.save(key=storage_key, content=content_bytes)

        version = await self.document_repo.create_version(
            document_id=document.id,
            version_number=1,
            storage_key=storage_key,
            original_filename=None,
            content_type="text/plain",
            size_bytes=len(content_bytes),
        )
        version = await self.document_repo.create_version(
            document_id=document.id,
            version_number=1,
            storage_key=storage_key,
            original_filename=None,
            content_type="text/plain",
            size_bytes=len(content_bytes),
        )
        process_document_version.delay(str(version.id))
        return document, version
        


class CreateDocumentFromUrlUseCase:
    def __init__(
        self,
        workspace_repo: WorkspaceRepository,
        document_repo: DocumentRepository,
        storage: StorageInterface,
    ):
        self.workspace_repo = workspace_repo
        self.document_repo = document_repo
        self.storage = storage

    async def execute(
        self, *, owner_id: UUID, workspace_id: UUID, url: str
    ) -> tuple[Document, DocumentVersion]:
        await GetWorkspaceUseCase(self.workspace_repo).execute(owner_id=owner_id, workspace_id=workspace_id)

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ValidationAppError(f"Could not fetch URL: {exc}") from exc

        content_bytes = response.content
        if len(content_bytes) > MAX_UPLOAD_BYTES:
            raise ValidationAppError(f"Fetched content exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit")

        document = await self.document_repo.create_document(
            workspace_id=workspace_id, title=url, source_type="url"
        )
        storage_key = generate_storage_key(
            workspace_id=str(workspace_id), document_id=str(document.id), filename="source.html"
        )
        self.storage.save(key=storage_key, content=content_bytes)

        version = await self.document_repo.create_version(
            document_id=document.id,
            version_number=1,
            storage_key=storage_key,
            original_filename=None,
            content_type=response.headers.get("content-type"),
            size_bytes=len(content_bytes),
        )
        version = await self.document_repo.create_version(
            document_id=document.id,
            version_number=1,
            storage_key=storage_key,
            original_filename=None,
            content_type=response.headers.get("content-type"),
            size_bytes=len(content_bytes),
        )
        process_document_version.delay(str(version.id))
        return document, version
        


class ListDocumentsUseCase:
    def __init__(self, workspace_repo: WorkspaceRepository, document_repo: DocumentRepository):
        self.workspace_repo = workspace_repo
        self.document_repo = document_repo

    async def execute(self, *, owner_id: UUID, workspace_id: UUID) -> list[Document]:
        await GetWorkspaceUseCase(self.workspace_repo).execute(owner_id=owner_id, workspace_id=workspace_id)
        return await self.document_repo.list_documents(workspace_id)


class GetDocumentUseCase:
    def __init__(self, workspace_repo: WorkspaceRepository, document_repo: DocumentRepository):
        self.workspace_repo = workspace_repo
        self.document_repo = document_repo

    async def execute(
        self, *, owner_id: UUID, workspace_id: UUID, document_id: UUID
    ) -> tuple[Document, list[DocumentVersion]]:
        await GetWorkspaceUseCase(self.workspace_repo).execute(owner_id=owner_id, workspace_id=workspace_id)
        document = await self.document_repo.get_document_by_id(document_id)
        if not document or document.workspace_id != workspace_id:
            from app.core.exceptions import NotFoundError

            raise NotFoundError("Document not found")
        versions = await self.document_repo.list_versions(document_id)
        return document, versions
