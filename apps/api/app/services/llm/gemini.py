from typing import AsyncIterator
import google.generativeai as genai

from app.core.config import settings
from app.services.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    name = "gemini"
    model = "gemini-2.0-flash"

    def _get_model(self):
        genai.configure(api_key=settings.gemini_api_key)
        return genai.GenerativeModel(self.model)

    async def generate(self, prompt: str, max_tokens: int = 2048) -> str:
        if not settings.gemini_api_key:
            return "GEMINI_API_KEY가 설정되지 않았습니다."
        model = self._get_model()
        response = await model.generate_content_async(
            prompt,
            generation_config={"max_output_tokens": max_tokens},
        )
        return response.text

    async def stream(self, prompt: str, max_tokens: int = 2048) -> AsyncIterator[str]:
        if not settings.gemini_api_key:
            yield "GEMINI_API_KEY가 설정되지 않았습니다."
            return
        model = self._get_model()
        async for chunk in await model.generate_content_async(
            prompt,
            stream=True,
            generation_config={"max_output_tokens": max_tokens},
        ):
            if chunk.text:
                yield chunk.text
