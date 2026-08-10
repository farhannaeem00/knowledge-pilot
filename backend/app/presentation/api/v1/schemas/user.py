"""
Pydantic response schema for user data. Never includes password_hash.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict,Field    


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str | None
    avatar_url: str | None
    role: str
    is_email_verified: bool
    created_at: datetime

class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(default=None, max_length=1024)
    bio: str | None = Field(default=None, max_length=1000)