from typing import Literal

from pydantic import BaseModel


class SearchResultOut(BaseModel):
    result_type: Literal["document_chunk", "note", "summary"]
    id: str
    workspace_id: str
    document_id: str | None
    title: str
    snippet: str
    score: float


class SearchResponse(BaseModel):
    query: str
    mode: Literal["semantic", "keyword", "hybrid"]
    results: list[SearchResultOut]