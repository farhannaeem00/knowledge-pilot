from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

Platform = Literal["youtube", "linkedin", "instagram_reel", "tiktok", "podcast", "presentation"]


class GenerateScriptRequest(BaseModel):
    platform: Platform


class ScriptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    document_id: UUID
    platform: str
    status: str
    error_message: str | None = None
    content_json: dict[str, Any] | None = None
    model_used: str | None = None
    created_at: datetime