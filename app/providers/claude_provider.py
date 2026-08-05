from .base import BaseProvider, LLMResult
from app import config


class ClaudeProvider(BaseProvider):
    name = "claude"

    def is_configured(self) -> bool:
        return bool(config.ANTHROPIC_API_KEY)

    def generate(self, system_prompt: str, messages: list[dict]) -> LLMResult:
        if not self.is_configured():
            return LLMResult(text="", error="ANTHROPIC_API_KEY is not set (add it to .env).")
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            resp = client.messages.create(
                model=config.CLAUDE_MODEL,
                system=system_prompt,
                messages=messages,
                max_tokens=700,
                temperature=0.3,
            )
            text = "".join(block.text for block in resp.content if block.type == "text")
            return LLMResult(text=text, raw_model=config.CLAUDE_MODEL)
        except Exception as e:
            return LLMResult(text="", error=f"Claude call failed: {e}")
