"""
Audit log persistence - async only, since all audit-worthy actions in
this app happen in synchronous API request handlers, not Celery tasks.
"""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        *,
        user_id: UUID | None,
        action: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        ip_address: str | None = None,
        details: dict | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            details=details,
        )
        self.session.add(entry)
        await self.session.commit()
        return entry