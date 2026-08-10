"""
Groq implementation of AIProviderInterface.

Groq's API is OpenAI-compatible, so we use the official `openai` SDK
pointed at Groq's base URL rather than a bespoke HTTP client - less code,
well-tested request/response handling.
"""
from openai import AsyncOpenAI

from app.application.interfaces.ai_provider import AIProviderInterface
from app.core.config import settings

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


class GroqProvider(AIProviderInterface):
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_GROQ_MODEL):
        self.client = AsyncOpenAI(api_key=api_key or settings.GROQ_API_KEY, base_url=GROQ_BASE_URL)
        self.model = model

    async def generate(
        self, *, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.3
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""