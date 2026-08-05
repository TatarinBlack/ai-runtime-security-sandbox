"""
Common interface every LLM provider implements.
Purpose: main.py and the security layer don't need to know which provider is
being called -- they all satisfy the same generate(system, messages) contract.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LLMResult:
    text: str
    raw_model: str = ""
    error: str | None = None
    # Simple "tool call" simulation: tool calls are parsed out of the final
    # answer text by security/tools.py using a regex pattern. This could be
    # wired to real function-calling APIs; a text-based pattern keeps the
    # demo consistent across all providers.
    tool_calls: list[dict] = field(default_factory=list)


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate(self, system_prompt: str, messages: list[dict]) -> LLMResult:
        """messages: [{"role": "user"/"assistant", "content": str}, ...]"""
        raise NotImplementedError

    def is_configured(self) -> bool:
        return True
