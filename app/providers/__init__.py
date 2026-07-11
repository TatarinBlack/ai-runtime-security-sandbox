from .base import BaseProvider, LLMResult
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .gemini_provider import GeminiProvider
from .custom_provider import CustomProvider
from .mock_provider import MockProvider

REGISTRY: dict[str, BaseProvider] = {
    "openai": OpenAIProvider(),
    "claude": ClaudeProvider(),
    "gemini": GeminiProvider(),
    "custom": CustomProvider(),
    "mock": MockProvider(),
}


def get_provider(name: str) -> BaseProvider:
    provider = REGISTRY.get(name)
    if provider is None:
        raise ValueError(f"Bilinmeyen provider: {name}")
    return provider


def list_providers() -> list[dict]:
    return [
        {"id": p.name, "configured": p.is_configured()}
        for p in REGISTRY.values()
    ]
