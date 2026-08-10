"""
FastAPI dependency wiring - the composition root for the presentation layer.
"""
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.infrastructure.db.models.user import User
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository
from app.infrastructure.storage.local_storage import LocalStorage
from app.infrastructure.repositories.document_chunk_repository import DocumentChunkRepository
from app.infrastructure.repositories.summary_repository import SummaryRepository
from app.infrastructure.repositories.chat_repository import ChatRepository

from app.infrastructure.repositories.highlight_repository import HighlightRepository
from app.infrastructure.repositories.note_repository import NoteRepository

from app.infrastructure.repositories.script_repository import ScriptRepository

from app.infrastructure.repositories.collection_repository import CollectionRepository
from app.infrastructure.repositories.folder_repository import FolderRepository

from app.infrastructure.repositories.notification_repository import NotificationRepository

from app.core.exceptions import ForbiddenError
from app.infrastructure.repositories.ai_usage_repository import AIUsageRepository
from app.infrastructure.repositories.audit_log_repository import AuditLogRepository


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


def get_refresh_token_repository(session: AsyncSession = Depends(get_db)) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


def get_workspace_repository(session: AsyncSession = Depends(get_db)) -> WorkspaceRepository:
    return WorkspaceRepository(session)


def get_document_repository(session: AsyncSession = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(session)


def get_storage() -> LocalStorage:
    return LocalStorage()


async def get_current_user(
    authorization: str | None = Header(default=None),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing or malformed Authorization header")

    token = authorization.split(" ", 1)[1]
    user_id = decode_access_token(token)
    if not user_id:
        raise UnauthorizedError("Invalid or expired access token")

    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    return user


def get_document_chunk_repository(session: AsyncSession = Depends(get_db)) -> DocumentChunkRepository:
    return DocumentChunkRepository(session)

def get_summary_repository(session: AsyncSession = Depends(get_db)) -> SummaryRepository:
    return SummaryRepository(session)

def get_chat_repository(session: AsyncSession = Depends(get_db)) -> ChatRepository:
    return ChatRepository(session)

def get_note_repository(session: AsyncSession = Depends(get_db)) -> NoteRepository:
    return NoteRepository(session)


def get_highlight_repository(session: AsyncSession = Depends(get_db)) -> HighlightRepository:
    return HighlightRepository(session)

def get_script_repository(session: AsyncSession = Depends(get_db)) -> ScriptRepository:
    return ScriptRepository(session)

def get_folder_repository(session: AsyncSession = Depends(get_db)) -> FolderRepository:
    return FolderRepository(session)


def get_collection_repository(session: AsyncSession = Depends(get_db)) -> CollectionRepository:
    return CollectionRepository(session)

def get_notification_repository(session: AsyncSession = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(session)

def get_ai_usage_repository(session: AsyncSession = Depends(get_db)) -> AIUsageRepository:
    return AIUsageRepository(session)


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise ForbiddenError("Admin access required")
    return current_user
def get_audit_log_repository(session: AsyncSession = Depends(get_db)) -> AuditLogRepository:
    return AuditLogRepository(session)