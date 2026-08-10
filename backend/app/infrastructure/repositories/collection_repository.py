from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.collection import Collection
from app.infrastructure.db.models.collection_item import CollectionItem
from app.infrastructure.db.models.document import Document


class CollectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, workspace_id: UUID, name: str) -> Collection:
        collection = Collection(workspace_id=workspace_id, name=name)
        self.session.add(collection)
        await self.session.commit()
        await self.session.refresh(collection)
        return collection

    async def get_by_id(self, collection_id: UUID) -> Collection | None:
        result = await self.session.execute(select(Collection).where(Collection.id == collection_id))
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: UUID) -> list[Collection]:
        result = await self.session.execute(
            select(Collection).where(Collection.workspace_id == workspace_id).order_by(Collection.name)
        )
        return list(result.scalars().all())

    async def delete(self, collection: Collection) -> None:
        await self.session.delete(collection)
        await self.session.commit()

    async def add_document(self, *, collection_id: UUID, document_id: UUID) -> CollectionItem:
        item = CollectionItem(collection_id=collection_id, document_id=document_id)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def remove_document(self, *, collection_id: UUID, document_id: UUID) -> None:
        await self.session.execute(
            delete(CollectionItem).where(
                CollectionItem.collection_id == collection_id, CollectionItem.document_id == document_id
            )
        )
        await self.session.commit()

    async def list_documents(self, collection_id: UUID) -> list[Document]:
        result = await self.session.execute(
            select(Document)
            .join(CollectionItem, CollectionItem.document_id == Document.id)
            .where(CollectionItem.collection_id == collection_id)
        )
        return list(result.scalars().all())