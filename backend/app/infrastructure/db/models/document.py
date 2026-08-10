"""
Document ORM model. Belongs to a Workspace, optionally to a Folder.
Carries tags/favorite/status directly (lightweight org layer, same
pattern as Note.tags) rather than extra join tables for v1.
"""
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin, UUIDMixin


class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "documents"

    workspace_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    folder_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("folders.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # source_type: pdf | docx | txt | md | url | paste

    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    # status: active | archived | trashed

    def __repr__(self) -> str:
        return f"<Document id={self.id} title={self.title}>"