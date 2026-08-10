"""
Notification endpoints. Polling-based delivery for v1 (frontend calls
GET periodically) - matches the MoSCoW "Should" (not "Must") priority
for live WebSocket/SSE updates.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.infrastructure.db.models.user import User
from app.infrastructure.repositories.notification_repository import NotificationRepository
from app.presentation.api.v1.schemas.notification import NotificationOut, UnreadCountOut
from app.presentation.dependencies import get_current_user, get_notification_repository

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
async def list_notifications(
    unread_only: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    notification_repo: NotificationRepository = Depends(get_notification_repository),
) -> list[NotificationOut]:
    notifications = await notification_repo.list_for_user(current_user.id, unread_only=unread_only)
    return [NotificationOut.model_validate(n) for n in notifications]


@router.get("/unread-count", response_model=UnreadCountOut)
async def unread_count(
    current_user: User = Depends(get_current_user),
    notification_repo: NotificationRepository = Depends(get_notification_repository),
) -> UnreadCountOut:
    count = await notification_repo.count_unread(current_user.id)
    return UnreadCountOut(unread_count=count)


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    notification_repo: NotificationRepository = Depends(get_notification_repository),
) -> None:
    await notification_repo.mark_read(user_id=current_user.id, notification_id=notification_id)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    notification_repo: NotificationRepository = Depends(get_notification_repository),
) -> None:
    await notification_repo.mark_all_read(current_user.id)