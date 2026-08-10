"""
Search service: semantic (pgvector), keyword (Postgres full-text search),
and hybrid (union + normalized combined score).
Every query is joined through workspace ownership - this is the actual
enforcement of "no cross-user data leakage" for search, not just a
documented intention. No stored tsvector column is used (avoids a
migration + trigger for v1); to_tsvector is computed on the fly, which
is perfectly adequate at this data volume.
"""
from dataclasses import dataclass
from uuid import UUID
from sqlalchemy import String, cast, func, literal, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.document import Document
from app.infrastructure.db.models.document_chunk import DocumentChunk
from app.infrastructure.db.models.document_version import DocumentVersion
from app.infrastructure.db.models.embedding import Embedding
from app.infrastructure.db.models.note import Note
from app.infrastructure.db.models.summary import Summary
from app.infrastructure.db.models.workspace import Workspace
from app.infrastructure.embeddings.local_embedder import embed_query


@dataclass
class SearchResult:
    result_type: str  # document_chunk | note | summary
    id: str
    workspace_id: str
    document_id: str | None
    title: str
    snippet: str
    score: float  # higher = more relevant, normalized 0-1 across result types


async def semantic_search(
    session: AsyncSession, *, owner_id: UUID, query: str, limit: int = 10
) -> list[SearchResult]:
    query_vector = embed_query(query)

    stmt = (
        select(
            DocumentChunk.id,
            DocumentChunk.content,
            Document.id.label("document_id"),
            Document.title,
            Document.workspace_id,
            Embedding.vector.cosine_distance(query_vector).label("distance"),
        )
        .join(Embedding, Embedding.chunk_id == DocumentChunk.id)
        .join(DocumentVersion, DocumentVersion.id == DocumentChunk.version_id)
        .join(Document, Document.id == DocumentVersion.document_id)
        .join(Workspace, Workspace.id == Document.workspace_id)
        .where(Workspace.owner_id == owner_id, DocumentVersion.is_current.is_(True))
        .order_by("distance")
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()

    results = []
    for chunk_id, content, document_id, title, workspace_id, distance in rows:
        # cosine_distance ranges 0 (identical) to 2 (opposite); convert to a 0-1 score.
        score = max(0.0, 1.0 - (distance / 2.0))
        results.append(
            SearchResult(
                result_type="document_chunk",
                id=str(chunk_id),
                workspace_id=str(workspace_id),
                document_id=str(document_id),
                title=title,
                snippet=content[:300],
                score=score,
            )
        )
    return results


async def keyword_search_documents(
    session: AsyncSession, *, owner_id: UUID, query: str, limit: int = 10
) -> list[SearchResult]:
    ts_query = func.plainto_tsquery("english", query)
    rank = func.ts_rank(func.to_tsvector("english", DocumentChunk.content), ts_query).label("rank")

    stmt = (
        select(
            DocumentChunk.id,
            DocumentChunk.content,
            Document.id.label("document_id"),
            Document.title,
            Document.workspace_id,
            rank,
        )
        .join(DocumentVersion, DocumentVersion.id == DocumentChunk.version_id)
        .join(Document, Document.id == DocumentVersion.document_id)
        .join(Workspace, Workspace.id == Document.workspace_id)
        .where(
            Workspace.owner_id == owner_id,
            DocumentVersion.is_current.is_(True),
            func.to_tsvector("english", DocumentChunk.content).op("@@")(ts_query),
        )
        .order_by(rank.desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()

    max_rank = max((r[-1] for r in rows), default=1.0) or 1.0
    results = []
    for chunk_id, content, document_id, title, workspace_id, rank_value in rows:
        results.append(
            SearchResult(
                result_type="document_chunk",
                id=str(chunk_id),
                workspace_id=str(workspace_id),
                document_id=str(document_id),
                title=title,
                snippet=content[:300],
                score=float(rank_value) / float(max_rank),
            )
        )
    return results


async def keyword_search_notes(
    session: AsyncSession, *, owner_id: UUID, query: str, limit: int = 10
) -> list[SearchResult]:
    ts_query = func.plainto_tsquery("english", query)
    searchable = func.to_tsvector("english", Note.title + " " + Note.content_md)
    rank = func.ts_rank(searchable, ts_query).label("rank")

    stmt = (
        select(Note.id, Note.title, Note.content_md, Note.workspace_id, Note.document_id, rank)
        .join(Workspace, Workspace.id == Note.workspace_id)
        .where(Workspace.owner_id == owner_id, searchable.op("@@")(ts_query))
        .order_by(rank.desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()

    max_rank = max((r[-1] for r in rows), default=1.0) or 1.0
    results = []
    for note_id, title, content_md, workspace_id, document_id, rank_value in rows:
        results.append(
            SearchResult(
                result_type="note",
                id=str(note_id),
                workspace_id=str(workspace_id),
                document_id=str(document_id) if document_id else None,
                title=title,
                snippet=content_md[:300],
                score=float(rank_value) / float(max_rank),
            )
        )
    return results


async def keyword_search_summaries(
    session: AsyncSession, *, owner_id: UUID, query: str, limit: int = 10
) -> list[SearchResult]:
    ts_query = func.plainto_tsquery("english", query)
    # content_json is JSONB; cast the "overview" field to text for full-text search.
    overview_text = cast(Summary.content_json["overview"], String)
    searchable = func.to_tsvector("english", func.coalesce(overview_text, ""))
    rank = func.ts_rank(searchable, ts_query).label("rank")

    stmt = (
        select(
            Summary.id,
            overview_text,
            DocumentVersion.document_id,
            Document.title,
            Document.workspace_id,
            rank,
        )
        .join(DocumentVersion, DocumentVersion.id == Summary.version_id)
        .join(Document, Document.id == DocumentVersion.document_id)
        .join(Workspace, Workspace.id == Document.workspace_id)
        .where(
            Workspace.owner_id == owner_id,
            Summary.is_active.is_(True),
            Summary.status == "done",
            searchable.op("@@")(ts_query),
        )
        .order_by(rank.desc())
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()

    max_rank = max((r[-1] for r in rows), default=1.0) or 1.0
    results = []
    for summary_id, overview, document_id, title, workspace_id, rank_value in rows:
        results.append(
            SearchResult(
                result_type="summary",
                id=str(summary_id),
                workspace_id=str(workspace_id),
                document_id=str(document_id),
                title=title,
                snippet=(overview or "")[:300],
                score=float(rank_value) / float(max_rank),
            )
        )
    return results


async def hybrid_search(
    session: AsyncSession, *, owner_id: UUID, query: str, limit: int = 15
) -> list[SearchResult]:
    """
    Union of semantic + keyword (documents, notes, summaries), deduplicated
    by (result_type, id), sorted by score descending. Simple and effective
    for v1 rather than reciprocal-rank-fusion.
    """
    semantic_results = await semantic_search(session, owner_id=owner_id, query=query, limit=limit)
    keyword_doc_results = await keyword_search_documents(session, owner_id=owner_id, query=query, limit=limit)
    note_results = await keyword_search_notes(session, owner_id=owner_id, query=query, limit=limit)
    summary_results = await keyword_search_summaries(session, owner_id=owner_id, query=query, limit=limit)

    seen: dict[tuple[str, str], SearchResult] = {}
    for result in semantic_results + keyword_doc_results + note_results + summary_results:
        key = (result.result_type, result.id)
        if key not in seen or result.score > seen[key].score:
            seen[key] = result

    combined = sorted(seen.values(), key=lambda r: r.score, reverse=True)
    return combined[:limit]