"""
Deterministic, character-based chunking with overlap.

Character-based (not token-based) for now - simple, free, no tokenizer
dependency. Once a specific embedding model is chosen in Step 5b, this
can be swapped for token-aware chunking without touching the pipeline
task, since chunk_text() is the only entry point callers depend on.
"""
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def chunk_text(text: str, *, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(current)
            if len(para) > chunk_size:
                for i in range(0, len(para), chunk_size - overlap):
                    chunks.append(para[i : i + chunk_size])
                current = ""
            else:
                current = para

    if current:
        chunks.append(current)

    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-overlap:]
            overlapped.append(f"{prev_tail}\n\n{chunks[i]}")
        return overlapped

    return chunks
