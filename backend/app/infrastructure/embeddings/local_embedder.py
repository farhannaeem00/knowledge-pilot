"""
Local embedding generation via sentence-transformers.

Model is loaded once per worker process (module-level singleton) since
loading it per-task would be extremely slow - the model stays resident
in memory for the life of the worker process.
"""
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "BAAI/bge-base-en-v1.5"
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    bge models recommend no special prefix for passages (only queries get
    a 'query: ' style prefix for some bge variants) - bge-base-en-v1.5
    specifically only needs a prefix on the query side, not documents, so
    we embed chunk text as-is here.
    """
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    """Query-side embedding - bge models recommend this instruction prefix for queries."""
    model = _get_model()
    prefixed = f"Represent this sentence for searching relevant passages: {query}"
    vector = model.encode([prefixed], normalize_embeddings=True, show_progress_bar=False)
    return vector[0].tolist()