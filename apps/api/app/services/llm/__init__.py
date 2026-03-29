from app.services.llm.base import LLMProvider
from app.services.llm.claude import ClaudeProvider
from app.services.llm.openai import OpenAIProvider
from app.services.llm.gemini import GeminiProvider

__all__ = ["LLMProvider", "ClaudeProvider", "OpenAIProvider", "GeminiProvider"]


def get_provider(name: str) -> LLMProvider:
    providers = {
        "claude": ClaudeProvider,
        "gpt": OpenAIProvider,
        "gemini": GeminiProvider,
    }
    cls = providers.get(name.lower())
    if cls is None:
        raise ValueError(f"지원하지 않는 LLM: {name}. 선택 가능: {list(providers.keys())}")
    return cls()
