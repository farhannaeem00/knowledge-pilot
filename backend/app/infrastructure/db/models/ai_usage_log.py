"""
AIUsageLog ORM model. One row per AI provider call, across every feature
(summary, script, chat). Billing is deferred, but this data is captured
from day one per the requirements review decision - cheap to log now,
expensive to reconstruct retroactively later.
"""
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin, UUIDMixin


class AIUsageLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_usage_logs"

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    workspace_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True
    )
    feature: Mapped[str] = mapped_column(String(30), nullable=False)
    # feature: summary | script | chat | embedding

    provider: Mapped[str] = mapped_column(String(30), nullable=False, default="groq")
    model: Mapped[str] = mapped_column(String(100), nullable=False)

    tokens_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_out: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Groq's free tier = $0 actual cost; estimated_cost_usd is populated as
    # 0.0 for now but the field exists so a future paid-tier switch (or a
    # different provider) doesn't need a migration.

    def __repr__(self) -> str:
        return f"<AIUsageLog id={self.id} feature={self.feature} model={self.model}>"