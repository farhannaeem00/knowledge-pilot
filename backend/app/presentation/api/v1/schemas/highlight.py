from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

HighlightLevel = Literal["must_read", "important", "optional", "custom"]


class HighlightCreate(BaseModel):
    level: HighlightLevel = "important"
    start_offset: int = Field(ge=0)
    end_offset: int = Field(gt=0)
    highlighted_text: str = Field(min_length=1)
    note: str | None = None


class HighlightOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version_id: UUID
    level: str
    start_offset: int
    end_offset: int
    highlighted_text: str
    note: str | None
    created_at: datetime