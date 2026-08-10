"""
Concrete Postgres implementation for Document + DocumentVersion persistence.
"""
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.document import Document
from app.infrastructure.db.models.document_version import DocumentVersion


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(self, *, workspace_id: UUID, title: str, source_type: str) -> Document:
        document = Document(workspace_id=workspace_id, title=title, source_type=source_type)
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_document_by_id(self, document_id: UUID) -> Document | None:
        result = await self.session.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def list_documents(self, workspace_id: UUID) -> list[Document]:
        result = await self.session.execute(
            select(Document)
            .where(Document.workspace_id == workspace_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_next_version_number(self, document_id: UUID) -> int:
        result = await self.session.execute(
            select(DocumentVersion.version_number)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()
        return (latest or 0) + 1

    async def create_version(
        self,
        *,
        document_id: UUID,
        version_number: int,
        storage_key: str,
        original_filename: str | None,
        content_type: str | None,
        size_bytes: int,
    ) -> DocumentVersion:
        # Unset is_current on all prior versions of this document, then
        # insert the new one as current - this is what "never overwrite,
        # keep history" actually means at the data layer.
        await self.session.execute(
            update(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .values(is_current=False)
        )
        version = DocumentVersion(
            document_id=document_id,
            version_number=version_number,
            is_current=True,
            storage_key=storage_key,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=size_bytes,
            status="uploaded",
        )
        self.session.add(version)
        await self.session.commit()
        await self.session.refresh(version)
        return version

    async def list_versions(self, document_id: UUID) -> list[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
        )
        return list(result.scalars().all())

    async def get_current_version(self, document_id: UUID) -> DocumentVersion | None:
        result = await self.session.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == document_id, DocumentVersion.is_current.is_(True)
            )
        )
        return result.scalar_one_or_none()

    async def update(self, document: Document, **fields) -> Document:
        for key, value in fields.items():
            if value is not None:
                setattr(document, key, value)
        await self.session.commit()
        await self.session.refresh(document)
        return document