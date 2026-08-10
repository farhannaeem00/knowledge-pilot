from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

SummaryStyle = Literal[
    "executive", "beginner", "technical", "bullet_points", "detailed", "academic", "content_creator"
]


class GenerateSummaryRequest(BaseModel):
    style: SummaryStyle = "detailed"


class SummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version_id: UUID
    style: str
    status: str
    error_message: str | None = None
    content_json: dict[str, Any] | None = None
    is_active: bool
    model_used: str | None = None
    created_at: datetime
