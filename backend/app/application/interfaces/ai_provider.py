"""
AI generation provider port. Chat/summarization use cases (Step 6+)
depend on this Protocol, never on a concrete provider SDK. Swapping
Groq -> OpenAI -> Anthropic -> local Ollama later means writing a new
class here and changing one line in dependency wiring - zero changes
to use case code.
"""
from typing import Protocol


class AIProviderInterface(Protocol):
    async def generate(
        self, *, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.3
    ) -> str:
        """Returns the generated text response."""
        ...