"""
Chat thread + message persistence (async - chat is a synchronous
request/response flow from FastAPI, not a Celery task).
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.chat_message import ChatMessage
from app.infrastructure.db.models.chat_thread import ChatThread


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_thread(self, *, workspace_id: UUID, document_id: UUID, title: str) -> ChatThread:
        thread = ChatThread(workspace_id=workspace_id, document_id=document_id, title=title)
        self.session.add(thread)
        await self.session.commit()
        await self.session.refresh(thread)
        return thread

    async def get_thread(self, thread_id: UUID) -> ChatThread | None:
        result = await self.session.execute(select(ChatThread).where(ChatThread.id == thread_id))
        return result.scalar_one_or_none()

    async def list_threads(self, workspace_id: UUID, document_id: UUID) -> list[ChatThread]:
        result = await self.session.execute(
            select(ChatThread)
            .where(ChatThread.workspace_id == workspace_id, ChatThread.document_id == document_id)
            .order_by(ChatThread.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_message(
        self, *, thread_id: UUID, role: str, content: str, retrieved_chunk_ids: list[str] | None = None
    ) -> ChatMessage:
        message = ChatMessage(
            thread_id=thread_id, role=role, content=content, retrieved_chunk_ids=retrieved_chunk_ids
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def list_messages(self, thread_id: UUID) -> list[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage).where(ChatMessage.thread_id == thread_id).order_by(ChatMessage.created_at)
        )
        return list(result.scalars().all())