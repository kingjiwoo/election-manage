"""LLM 프로바이더 추상 인터페이스"""
from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def model(self) -> str: ...

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 2048) -> str: ...

    @abstractmethod
    async def stream(self, prompt: str, max_tokens: int = 2048) -> AsyncIterator[str]: ...
