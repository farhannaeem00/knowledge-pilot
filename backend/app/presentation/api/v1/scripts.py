"""
Script endpoints - async generation (Celery), same pattern as summaries.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.exceptions import NotFoundError
from app.infrastructure.db.models.user import User
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.script_repository import ScriptRepository
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository
from app.infrastructure.tasks.script_tasks import generate_script
from app.presentation.api.v1.schemas.script import GenerateScriptRequest, ScriptOut
from app.presentation.dependencies import (
    get_current_user,
    get_document_repository,
    get_script_repository,
    get_workspace_repository,
)

router = APIRouter(prefix="/workspaces/{workspace_id}/documents/{document_id}/scripts", tags=["scripts"])


async def _verify_access(*, owner_id: UUID, workspace_id: UUID, document_id: UUID, workspace_repo, document_repo):
    workspace = await workspace_repo.get_by_id(workspace_id)
    if not workspace or workspace.owner_id != owner_id or workspace.status == "trashed":
        raise NotFoundError("Workspace not found")
    document = await document_repo.get_document_by_id(document_id)
    if not document or document.workspace_id != workspace_id:
        raise NotFoundError("Document not found")


@router.post("", response_model=ScriptOut, status_code=status.HTTP_202_ACCEPTED)
async def create_script(
    workspace_id: UUID,
    document_id: UUID,
    payload: GenerateScriptRequest,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    script_repo: ScriptRepository = Depends(get_script_repository),
) -> ScriptOut:
    await _verify_access(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    script = await script_repo.create_pending(
        workspace_id=workspace_id, document_id=document_id, platform=payload.platform
    )
    generate_script.delay(str(script.id))
    return ScriptOut.model_validate(script)


@router.get("", response_model=list[ScriptOut])
async def list_scripts(
    workspace_id: UUID,
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    script_repo: ScriptRepository = Depends(get_script_repository),
) -> list[ScriptOut]:
    await _verify_access(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    scripts = await script_repo.list_by_document(document_id)
    return [ScriptOut.model_validate(s) for s in scripts]


@router.get("/{script_id}", response_model=ScriptOut)
async def get_script(
    workspace_id: UUID,
    document_id: UUID,
    script_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    script_repo: ScriptRepository = Depends(get_script_repository),
) -> ScriptOut:
    await _verify_access(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    script = await script_repo.get_by_id(script_id)
    if not script or script.document_id != document_id:
        raise NotFoundError("Script not found")
    return ScriptOut.model_validate(script)