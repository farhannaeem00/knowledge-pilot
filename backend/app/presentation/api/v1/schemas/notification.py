from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    payload: dict[str, Any] | None
    read_at: datetime | None
    created_at: datetime


class UnreadCountOut(BaseModel):
    unread_count: int