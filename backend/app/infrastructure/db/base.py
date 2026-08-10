"""
Declarative base and reusable mixins for all ORM models.

Every table gets a UUID primary key (not an auto-increment int) because
IDs are exposed in URLs/APIs and UUIDs avoid leaking sequence/volume
information and make future multi-database sharding easier. Every table
also gets created_at/updated_at automatically via TimestampMixin so we
never forget to add auditing fields to a new model.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )