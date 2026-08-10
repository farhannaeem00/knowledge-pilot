"""
Notification persistence - both sync (for Celery tasks creating them) and
async (for the API reading/marking them read) variants.
"""
from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.infrastructure.db.models.notification import Notification


class SyncNotificationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, user_id: UUID, type_: str, payload: dict | None = None) -> Notification:
        notification = Notification(user_id=user_id, type=type_, payload=payload)
        self.session.add(notification)
        self.session.commit()
        return notification


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_for_user(self, user_id: UUID, *, unread_only: bool = False, limit: int = 50) -> list[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.read_at.is_(None))
        query = query.order_by(Notification.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_unread(self, user_id: UUID) -> int:
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        )
        return result.scalar_one()

    async def mark_read(self, *, user_id: UUID, notification_id: UUID) -> None:
        await self.session.execute(
            update(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
            .values(read_at=datetime.now(UTC))
        )
        await self.session.commit()

    async def mark_all_read(self, user_id: UUID) -> None:
        await self.session.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.read_at.is_(None))
            .values(read_at=datetime.now(UTC))
        )
        await self.session.commit()