"""
DocumentChunk ORM model - one row per chunk produced by the pipeline for
a given DocumentVersion. Deliberately has no embedding column yet -
chunking (free, deterministic) and embedding (costs API calls) are
separate concerns, wired together in Step 5b.
"""
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin, UUIDMixin


class DocumentChunk(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "document_chunks"

    version_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<DocumentChunk id={self.id} version_id={self.version_id} idx={self.chunk_index}>"
