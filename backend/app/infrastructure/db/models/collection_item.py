"""
CollectionItem - many-to-many join between Collection and Document.
"""
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin, UUIDMixin


class CollectionItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "collection_items"
    __table_args__ = (UniqueConstraint("collection_id", "document_id", name="uq_collection_document"),)

    collection_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )