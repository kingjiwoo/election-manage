from typing import AsyncIterator
from openai import AsyncOpenAI

from app.core.config import settings
from app.services.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    name = "gpt"
    model = "gpt-4o"

    def __init__(self):
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    async def generate(self, prompt: str, max_tokens: int = 2048) -> str:
        if not settings.openai_api_key:
            return "OPENAI_API_KEY가 설정되지 않았습니다."
        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""

    async def stream(self, prompt: str, max_tokens: int = 2048) -> AsyncIterator[str]:
        if not settings.openai_api_key:
            yield "OPENAI_API_KEY가 설정되지 않았습니다."
            return
        async with self.client.chat.completions.stream(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        ) as s:
            async for event in s:
                if event.type == "content.delta" and event.delta:
                    yield event.delta
