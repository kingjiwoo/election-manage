from typing import AsyncIterator
import anthropic

from app.core.config import settings
from app.services.llm.base import LLMProvider


class ClaudeProvider(LLMProvider):
    name = "claude"
    model = "claude-sonnet-4-6"

    def __init__(self):
        self._client: anthropic.AsyncAnthropic | None = None

    @property
    def client(self) -> anthropic.AsyncAnthropic:
        if self._client is None:
            self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def generate(self, prompt: str, max_tokens: int = 2048) -> str:
        if not settings.anthropic_api_key:
            return "ANTHROPIC_API_KEY가 설정되지 않았습니다."
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    async def stream(self, prompt: str, max_tokens: int = 2048) -> AsyncIterator[str]:
        if not settings.anthropic_api_key:
            yield "ANTHROPIC_API_KEY가 설정되지 않았습니다."
            return
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        ) as s:
            async for text in s.text_stream:
                yield text
