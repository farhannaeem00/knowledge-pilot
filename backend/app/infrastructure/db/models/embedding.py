"""
Embedding ORM model. One row per DocumentChunk. Kept as a separate table
(not a column on DocumentChunk) so the embedding model/dimension can
change independently of chunking, and so we can re-embed without
touching chunk rows.
"""
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.infrastructure.db.base import Base, TimestampMixin, UUIDMixin

EMBEDDING_DIM = 768  # BAAI/bge-base-en-v1.5 output dimension


class Embedding(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "embeddings"

    chunk_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    model: Mapped[str] = mapped_column(String(100), nullable=False, default="BAAI/bge-base-en-v1.5")
    vector: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)

    def __repr__(self) -> str:
        return f"<Embedding id={self.id} chunk_id={self.chunk_id}>"