"""
Summary endpoints. Generation is async (Celery) - POST returns
immediately with status "pending"; the client polls GET until status
becomes "done" or "failed" (SSE/WebSocket upgrade is a later step).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.exceptions import NotFoundError
from app.infrastructure.db.models.user import User
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.summary_repository import SummaryRepository
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository
from app.infrastructure.tasks.summary_tasks import generate_summary
from app.presentation.api.v1.schemas.summary import GenerateSummaryRequest, SummaryOut
from app.presentation.dependencies import (
    get_current_user,
    get_document_repository,
    get_summary_repository,
    get_workspace_repository,
)

router = APIRouter(prefix="/workspaces/{workspace_id}/documents/{document_id}", tags=["summaries"])


async def _verify_access(
    *, owner_id: UUID, workspace_id: UUID, document_id: UUID, workspace_repo, document_repo
):
    workspace = await workspace_repo.get_by_id(workspace_id)
    if not workspace or workspace.owner_id != owner_id or workspace.status == "trashed":
        raise NotFoundError("Workspace not found")
    document = await document_repo.get_document_by_id(document_id)
    if not document or document.workspace_id != workspace_id:
        raise NotFoundError("Document not found")
    version = await document_repo.get_current_version(document_id)
    if not version:
        raise NotFoundError("Document has no processed version yet")
    return version


@router.post("/summaries", response_model=SummaryOut, status_code=status.HTTP_202_ACCEPTED)
async def create_summary(
    workspace_id: UUID,
    document_id: UUID,
    payload: GenerateSummaryRequest,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    summary_repo: SummaryRepository = Depends(get_summary_repository),
) -> SummaryOut:
    version = await _verify_access(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )

    # Create the pending row via a sync-style insert done through the async
    # session here for API-layer consistency, then hand off to Celery.
    from app.infrastructure.db.models.summary import Summary
    from sqlalchemy import update as sa_update

    await summary_repo.session.execute(
        sa_update(Summary)
        .where(Summary.version_id == version.id, Summary.style == payload.style, Summary.is_active.is_(True))
        .values(is_active=False)
    )
    summary = Summary(version_id=version.id, style=payload.style, status="pending", is_active=True)
    summary_repo.session.add(summary)
    await summary_repo.session.commit()
    await summary_repo.session.refresh(summary)

    generate_summary.delay(str(summary.id))

    return SummaryOut.model_validate(summary)


@router.get("/summaries", response_model=list[SummaryOut])
async def list_summaries(
    workspace_id: UUID,
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    summary_repo: SummaryRepository = Depends(get_summary_repository),
) -> list[SummaryOut]:
    version = await _verify_access(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    summaries = await summary_repo.list_by_version(version.id)
    return [SummaryOut.model_validate(s) for s in summaries]


@router.get("/summaries/active", response_model=SummaryOut)
async def get_active_summary(
    workspace_id: UUID,
    document_id: UUID,
    style: str = "detailed",
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    summary_repo: SummaryRepository = Depends(get_summary_repository),
) -> SummaryOut:
    version = await _verify_access(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    summary = await summary_repo.get_active(version_id=version.id, style=style)
    if not summary:
        raise NotFoundError("No summary found for this style yet")
    return SummaryOut.model_validate(summary)