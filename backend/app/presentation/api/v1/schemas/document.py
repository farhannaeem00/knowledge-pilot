from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version_number: int
    is_current: bool
    original_filename: str | None
    content_type: str | None
    size_bytes: int
    status: str
    error_message: str | None = None
    chunk_count: int | None = None
    created_at: datetime


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    folder_id: UUID | None = None
    title: str
    source_type: str
    tags: list[str] | None = None
    is_favorite: bool = False
    status: str = "active"
    created_at: datetime
    updated_at: datetime


class DocumentWithVersionsOut(DocumentOut):
    versions: list[DocumentVersionOut]


class DocumentCreateFromUrl(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class DocumentCreateFromPaste(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    folder_id: UUID | None = None
    tags: list[str] | None = None
    is_favorite: bool | None = None
    status: str | None = None