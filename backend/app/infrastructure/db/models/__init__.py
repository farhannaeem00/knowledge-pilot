"""
Import every model here so Alembic's autogenerate sees the full schema.
"""
from app.infrastructure.db.models.ai_usage_log import AIUsageLog
from app.infrastructure.db.models.audit_log import AuditLog
from app.infrastructure.db.models.chat_message import ChatMessage
from app.infrastructure.db.models.chat_thread import ChatThread
from app.infrastructure.db.models.collection import Collection
from app.infrastructure.db.models.collection_item import CollectionItem
from app.infrastructure.db.models.document import Document
from app.infrastructure.db.models.document_chunk import DocumentChunk
from app.infrastructure.db.models.document_version import DocumentVersion
from app.infrastructure.db.models.embedding import Embedding
from app.infrastructure.db.models.folder import Folder
from app.infrastructure.db.models.highlight import Highlight
from app.infrastructure.db.models.note import Note
from app.infrastructure.db.models.notification import Notification
from app.infrastructure.db.models.refresh_token import RefreshToken
from app.infrastructure.db.models.script import Script
from app.infrastructure.db.models.summary import Summary
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.workspace import Workspace
from app.infrastructure.db.models.workspace_member import WorkspaceMember

__all__ = [
    "AIUsageLog",
    "AuditLog",
    "ChatMessage",
    "ChatThread",
    "Collection",
    "CollectionItem",
    "Document",
    "DocumentChunk",
    "DocumentVersion",
    "Embedding",
    "Folder",
    "Highlight",
    "Note",
    "Notification",
    "RefreshToken",
    "Script",
    "Summary",
    "User",
    "Workspace",
    "WorkspaceMember",
]