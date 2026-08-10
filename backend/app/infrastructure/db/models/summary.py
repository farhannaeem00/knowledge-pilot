"""
Summary ORM model. content_json holds the full structured summary
(overview, key ideas, section-wise, stats, pros/cons, etc.) as JSON
rather than one column per field - matches the spec's multi-part
structure without a migration every time we tweak it.

Regeneration in a different style creates a NEW row; it never overwrites
history (per the "save every AI output" requirement). is_active flags
the current one for a given (version_id, style) pair.
"""
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin, UUIDMixin


class Summary(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "summaries"

    version_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    style: Mapped[str] = mapped_column(String(30), nullable=False, default="detailed")
    # style: executive | beginner | technical | bullet_points | detailed | academic | content_creator

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    # status: pending | processing | done | failed
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    content_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<Summary id={self.id} version_id={self.version_id} style={self.style}>"
