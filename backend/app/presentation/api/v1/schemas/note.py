from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    document_id: UUID | None = None
    title: str = Field(default="Untitled Note", max_length=255)
    content_md: str = Field(default="")
    tags: list[str] | None = None


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    content_md: str | None = None
    tags: list[str] | None = None
    is_pinned: bool | None = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    document_id: UUID | None
    title: str
    content_md: str
    tags: list[str] | None
    is_pinned: bool
    created_at: datetime
    updated_at: datetime