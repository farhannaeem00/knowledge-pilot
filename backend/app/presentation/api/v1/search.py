"""
Search endpoint. Scoped strictly to the requesting user's own workspaces
via owner_id joins inside search_service - this is the enforcement point
for the "no cross-user data leakage" requirement, not just a comment.
"""
from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.user import User
from app.infrastructure.db.session import get_db
from app.infrastructure.search.search_service import hybrid_search, keyword_search_documents, semantic_search
from app.presentation.api.v1.schemas.search import SearchResponse, SearchResultOut
from app.presentation.dependencies import get_current_user

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1),
    mode: Literal["semantic", "keyword", "hybrid"] = "hybrid",
    limit: int = Query(default=15, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> SearchResponse:
    if mode == "semantic":
        results = await semantic_search(session, owner_id=current_user.id, query=q, limit=limit)
    elif mode == "keyword":
        results = await keyword_search_documents(session, owner_id=current_user.id, query=q, limit=limit)
    else:
        results = await hybrid_search(session, owner_id=current_user.id, query=q, limit=limit)

    return SearchResponse(
        query=q,
        mode=mode,
        results=[SearchResultOut(**r.__dict__) for r in results],
    )