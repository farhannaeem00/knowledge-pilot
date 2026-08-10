"""
Collection ORM model. A named, flat grouping of documents that can span
folders - distinct from Folder's strict hierarchy. Membership is
many-to-many via CollectionItem.
"""
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin, UUIDMixin


class Collection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "collections"

    workspace_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<Collection id={self.id} name={self.name}>"