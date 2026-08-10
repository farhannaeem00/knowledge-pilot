"""
AI usage log persistence - sync (for Celery tasks) and async (for admin
read endpoints) variants.
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.infrastructure.db.models.ai_usage_log import AIUsageLog


class SyncAIUsageRepository:
    def __init__(self, session: Session):
        self.session = session

    def log(
        self,
        *,
        user_id: UUID,
        workspace_id: UUID | None,
        feature: str,
        provider: str,
        model: str,
        tokens_in: int | None,
        tokens_out: int | None,
        latency_ms: int | None,
    ) -> AIUsageLog:
        entry = AIUsageLog(
            user_id=user_id,
            workspace_id=workspace_id,
            feature=feature,
            provider=provider,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            estimated_cost_usd=0.0,  # Groq free tier
        )
        self.session.add(entry)
        self.session.commit()
        return entry


class AIUsageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        *,
        user_id: UUID,
        workspace_id: UUID | None,
        feature: str,
        provider: str,
        model: str,
        tokens_in: int | None,
        tokens_out: int | None,
        latency_ms: int | None,
    ) -> AIUsageLog:
        entry = AIUsageLog(
            user_id=user_id,
            workspace_id=workspace_id,
            feature=feature,
            provider=provider,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            estimated_cost_usd=0.0,
        )
        self.session.add(entry)
        await self.session.commit()
        return entry

    async def summary_stats(self) -> dict:
        result = await self.session.execute(
            select(
                func.count().label("total_calls"),
                func.coalesce(func.sum(AIUsageLog.tokens_in), 0).label("total_tokens_in"),
                func.coalesce(func.sum(AIUsageLog.tokens_out), 0).label("total_tokens_out"),
                func.coalesce(func.avg(AIUsageLog.latency_ms), 0).label("avg_latency_ms"),
            )
        )
        row = result.one()
        return {
            "total_calls": row.total_calls,
            "total_tokens_in": row.total_tokens_in,
            "total_tokens_out": row.total_tokens_out,
            "avg_latency_ms": round(float(row.avg_latency_ms), 1),
        }

    async def by_feature(self) -> list[dict]:
        result = await self.session.execute(
            select(AIUsageLog.feature, func.count().label("count"))
            .group_by(AIUsageLog.feature)
            .order_by(func.count().desc())
        )
        return [{"feature": row.feature, "count": row.count} for row in result.all()]