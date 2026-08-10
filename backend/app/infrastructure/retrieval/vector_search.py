"""
Vector similarity search over a document version's chunks via pgvector's
cosine distance operator. This is the actual "R" in RAG - without this,
chat would just be an LLM guessing from its own training data instead of
being grounded in the uploaded document.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.document_chunk import DocumentChunk
from app.infrastructure.db.models.embedding import Embedding


async def search_similar_chunks(
    session: AsyncSession, *, version_id: UUID, query_vector: list[float], top_k: int = 5
) -> list[tuple[DocumentChunk, float]]:
    """
    Returns [(chunk, distance), ...] ordered by ascending cosine distance
    (0 = identical, 2 = opposite) - smaller distance means more relevant.
    Scoped to a single version_id, which is itself scoped to one document
    - this is what enforces "no cross-user/cross-document leakage" at the
    query level for chat/search.
    """
    stmt = (
        select(DocumentChunk, Embedding.vector.cosine_distance(query_vector).label("distance"))
        .join(Embedding, Embedding.chunk_id == DocumentChunk.id)
        .where(DocumentChunk.version_id == version_id)
        .order_by("distance")
        .limit(top_k)
    )
    result = await session.execute(stmt)
    return [(row[0], row[1]) for row in result.all()]