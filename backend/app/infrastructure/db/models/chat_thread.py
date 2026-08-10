"""
ChatThread ORM model. Multiple named threads per workspace, each scoped
to one document in v1 (multi-document chat is a v1.1 item per the
requirements review decision).
"""
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin, UUIDMixin


class ChatThread(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_threads"

    workspace_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New Chat")

    def __repr__(self) -> str:
        return f"<ChatThread id={self.id} title={self.title}>"