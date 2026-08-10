"""
Highlight ORM model. Anchored to a specific DocumentVersion's text via
character offsets - version-scoped rather than document-scoped, since
offsets become meaningless once the underlying text changes.
"""
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin, UUIDMixin


class Highlight(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "highlights"

    version_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="important")
    # level: must_read | important | optional | custom

    start_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    highlighted_text: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Highlight id={self.id} version_id={self.version_id} level={self.level}>"