"""
Chat endpoints: create thread, list threads, list messages, send message
(this last one does retrieval + Groq call synchronously and returns the
assistant's reply in the same response).
"""
from uuid import UUID
import time
from fastapi import APIRouter, Depends, status
from app.core.exceptions import NotFoundError
from app.infrastructure.ai_providers.groq_provider import GroqProvider
from app.infrastructure.db.models.user import User
from app.infrastructure.embeddings.local_embedder import embed_query
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.workspace_repository import WorkspaceRepository
from app.infrastructure.retrieval.vector_search import search_similar_chunks
from app.infrastructure.prompts.chat_prompts import CHAT_SYSTEM_PROMPT, build_context_block, build_user_turn
from app.presentation.api.v1.schemas.chat import (
    ChatMessageOut,
    ChatThreadOut,
    CreateThreadRequest,
    SendMessageRequest,
)
from app.presentation.dependencies import (
    get_chat_repository,
    get_current_user,
    get_document_repository,
    get_workspace_repository,
)
from app.infrastructure.repositories.ai_usage_repository import AIUsageRepository
from app.presentation.dependencies import get_ai_usage_repository

router = APIRouter(prefix="/workspaces/{workspace_id}/documents/{document_id}/chat", tags=["chat"])

TOP_K = 5


async def _verify_document_access(*, owner_id: UUID, workspace_id: UUID, document_id: UUID, workspace_repo, document_repo):
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


@router.post("/threads", response_model=ChatThreadOut, status_code=status.HTTP_201_CREATED)
async def create_thread(
    workspace_id: UUID,
    document_id: UUID,
    payload: CreateThreadRequest,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    chat_repo: ChatRepository = Depends(get_chat_repository),
) -> ChatThreadOut:
    await _verify_document_access(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    thread = await chat_repo.create_thread(workspace_id=workspace_id, document_id=document_id, title=payload.title)
    return ChatThreadOut.model_validate(thread)


@router.get("/threads", response_model=list[ChatThreadOut])
async def list_threads(
    workspace_id: UUID,
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    chat_repo: ChatRepository = Depends(get_chat_repository),
) -> list[ChatThreadOut]:
    await _verify_document_access(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    threads = await chat_repo.list_threads(workspace_id, document_id)
    return [ChatThreadOut.model_validate(t) for t in threads]


@router.get("/threads/{thread_id}/messages", response_model=list[ChatMessageOut])
async def list_messages(
    workspace_id: UUID,
    document_id: UUID,
    thread_id: UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    chat_repo: ChatRepository = Depends(get_chat_repository),
) -> list[ChatMessageOut]:
    await _verify_document_access(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    thread = await chat_repo.get_thread(thread_id)
    if not thread or thread.workspace_id != workspace_id or thread.document_id != document_id:
        raise NotFoundError("Chat thread not found")
    messages = await chat_repo.list_messages(thread_id)
    return [ChatMessageOut.model_validate(m) for m in messages]


@router.post("/threads/{thread_id}/messages", response_model=ChatMessageOut, status_code=status.HTTP_201_CREATED)
async def send_message(
    workspace_id: UUID,
    document_id: UUID,
    thread_id: UUID,
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
    chat_repo: ChatRepository = Depends(get_chat_repository),
    ai_usage_repo: AIUsageRepository = Depends(get_ai_usage_repository),
) -> ChatMessageOut:
    version = await _verify_document_access(
        owner_id=current_user.id,
        workspace_id=workspace_id,
        document_id=document_id,
        workspace_repo=workspace_repo,
        document_repo=document_repo,
    )
    thread = await chat_repo.get_thread(thread_id)
    if not thread or thread.workspace_id != workspace_id or thread.document_id != document_id:
        raise NotFoundError("Chat thread not found")

    # 1. Persist the user's message first, so it's never lost even if the AI call fails.
    await chat_repo.add_message(thread_id=thread_id, role="user", content=payload.content)

    # 2. Retrieve relevant chunks (the "R" in RAG) - grounds the answer in the actual document.
    query_vector = embed_query(payload.content)
    chunks_with_distance = await search_similar_chunks(
        chat_repo.session, version_id=version.id, query_vector=query_vector, top_k=TOP_K
    )
    context_block = build_context_block([(c.content, d) for c, d in chunks_with_distance])

    # 3. Include prior thread history so follow-ups like "compare it with X" resolve correctly.
    history = await chat_repo.list_messages(thread_id)
    history_messages = [{"role": m.role, "content": m.content} for m in history[:-1]]  # exclude the message just added

    provider = GroqProvider()
    messages_for_model = (
        [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
        + history_messages
        + [{"role": "user", "content": build_user_turn(question=payload.content, context_block=context_block)}]
    )

    start_time = time.monotonic()
    response = await provider.client.chat.completions.create(
        model=provider.model,
        messages=messages_for_model,
        max_tokens=1024,
        temperature=0.3,
    )
    latency_ms = int((time.monotonic() - start_time) * 1000)
    reply_text = response.choices[0].message.content or ""

    await ai_usage_repo.log(
        user_id=current_user.id,
        workspace_id=workspace_id,
        feature="chat",
        provider="groq",
        model=provider.model,
        tokens_in=response.usage.prompt_tokens if response.usage else None,
        tokens_out=response.usage.completion_tokens if response.usage else None,
        latency_ms=latency_ms,
    )

    assistant_message = await chat_repo.add_message(
        thread_id=thread_id,
        role="assistant",
        content=reply_text,
        retrieved_chunk_ids=[str(c.id) for c, _ in chunks_with_distance],
    )
    return ChatMessageOut.model_validate(assistant_message)