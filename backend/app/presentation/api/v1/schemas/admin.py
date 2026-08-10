from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str | None
    role: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime


class AdminDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    title: str
    source_type: str
    status: str
    created_at: datetime


class AIUsageSummaryOut(BaseModel):
    total_calls: int
    total_tokens_in: int
    total_tokens_out: int
    avg_latency_ms: float


class AIUsageByFeatureOut(BaseModel):
    feature: str
    count: int


class StorageStatsOut(BaseModel):
    total_documents: int
    total_versions: int
    total_size_bytes: int