from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateThreadRequest(BaseModel):
    title: str = Field(default="New Chat", max_length=255)


class ChatThreadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    document_id: UUID
    title: str
    created_at: datetime


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1)


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    thread_id: UUID
    role: str
    content: str
    created_at: datetime