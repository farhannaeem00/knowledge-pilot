"""
Embedding persistence (sync, for the Celery worker).
"""
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.infrastructure.db.models.embedding import Embedding


class SyncEmbeddingRepository:
    def __init__(self, session: Session):
        self.session = session

    def delete_by_chunk_ids(self, chunk_ids: list[UUID]) -> None:
        if not chunk_ids:
            return
        self.session.execute(delete(Embedding).where(Embedding.chunk_id.in_(chunk_ids)))
        self.session.commit()

    def bulk_create(self, *, chunk_ids: list[UUID], vectors: list[list[float]], model: str) -> None:
        objects = [
            Embedding(chunk_id=chunk_id, vector=vector, model=model)
            for chunk_id, vector in zip(chunk_ids, vectors, strict=True)
        ]
        self.session.add_all(objects)
        self.session.commit()