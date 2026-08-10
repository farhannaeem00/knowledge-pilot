"""
Admin endpoints. All routes here require role == "admin" via the
require_admin dependency - reuses the existing User.role field.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.document import Document
from app.infrastructure.db.models.document_version import DocumentVersion
from app.infrastructure.db.models.user import User
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.ai_usage_repository import AIUsageRepository
from app.presentation.api.v1.schemas.admin import (
    AdminDocumentOut,
    AdminUserOut,
    AIUsageByFeatureOut,
    AIUsageSummaryOut,
    StorageStatsOut,
)
from app.presentation.dependencies import get_ai_usage_repository, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUserOut])
async def list_users(
    _admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[AdminUserOut]:
    result = await session.execute(select(User).order_by(User.created_at.desc()))
    return [AdminUserOut.model_validate(u) for u in result.scalars().all()]


@router.get("/documents", response_model=list[AdminDocumentOut])
async def list_all_documents(
    _admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[AdminDocumentOut]:
    result = await session.execute(select(Document).order_by(Document.created_at.desc()).limit(200))
    return [AdminDocumentOut.model_validate(d) for d in result.scalars().all()]


@router.get("/storage", response_model=StorageStatsOut)
async def storage_stats(
    _admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> StorageStatsOut:
    doc_count = (await session.execute(select(func.count()).select_from(Document))).scalar_one()
    version_count = (await session.execute(select(func.count()).select_from(DocumentVersion))).scalar_one()
    total_size = (
        await session.execute(select(func.coalesce(func.sum(DocumentVersion.size_bytes), 0)))
    ).scalar_one()
    return StorageStatsOut(total_documents=doc_count, total_versions=version_count, total_size_bytes=total_size)


@router.get("/ai-usage/summary", response_model=AIUsageSummaryOut)
async def ai_usage_summary(
    _admin: User = Depends(require_admin),
    ai_usage_repo: AIUsageRepository = Depends(get_ai_usage_repository),
) -> AIUsageSummaryOut:
    stats = await ai_usage_repo.summary_stats()
    return AIUsageSummaryOut(**stats)


@router.get("/ai-usage/by-feature", response_model=list[AIUsageByFeatureOut])
async def ai_usage_by_feature(
    _admin: User = Depends(require_admin),
    ai_usage_repo: AIUsageRepository = Depends(get_ai_usage_repository),
) -> list[AIUsageByFeatureOut]:
    stats = await ai_usage_repo.by_feature()
    return [AIUsageByFeatureOut(**s) for s in stats]