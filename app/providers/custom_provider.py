from .base import BaseProvider, LLMResult
from app import config


class CustomProvider(BaseProvider):
    """Any OpenAI-compatible endpoint: Ollama, LM Studio, vLLM, Azure OpenAI, etc."""
    name = "custom"

    def is_configured(self) -> bool:
        return bool(config.CUSTOM_BASE_URL)

    def generate(self, system_prompt: str, messages: list[dict]) -> LLMResult:
        if not self.is_configured():
            return LLMResult(text="", error="CUSTOM_BASE_URL is not set (add it to .env).")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config.CUSTOM_API_KEY or "not-needed", base_url=config.CUSTOM_BASE_URL)
            resp = client.chat.completions.create(
                model=config.CUSTOM_MODEL,
                messages=[{"role": "system", "content": system_prompt}, *messages],
                temperature=0.3,
                max_tokens=700,
            )
            text = resp.choices[0].message.content or ""
            return LLMResult(text=text, raw_model=config.CUSTOM_MODEL)
        except Exception as e:
            return LLMResult(text="", error=f"Custom endpoint call failed: {e}")
