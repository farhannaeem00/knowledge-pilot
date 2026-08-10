"""
Prompt construction for RAG chat. The system prompt explicitly instructs
the model to answer only from retrieved context and say so when the
context doesn't cover the question - this is the actual grounding
mechanism, not just a nice-to-have instruction.
"""
CHAT_SYSTEM_PROMPT = """You are an AI assistant helping a user understand a specific document they've uploaded.

Answer using ONLY the provided document excerpts below. If the excerpts don't contain enough information to answer, say so honestly rather than guessing or using outside knowledge.

Be concise and direct. Reference specific parts of the document when relevant."""


def build_context_block(chunks_with_distance: list[tuple[str, float]]) -> str:
    if not chunks_with_distance:
        return "(No relevant excerpts were found in the document for this question.)"
    parts = []
    for i, (content, _distance) in enumerate(chunks_with_distance, start=1):
        parts.append(f"[Excerpt {i}]\n{content}")
    return "\n\n".join(parts)


def build_user_turn(*, question: str, context_block: str) -> str:
    return f"Document excerpts:\n{context_block}\n\nUser question: {question}"