from .base import BaseProvider, LLMResult
from app import config


class OpenAIProvider(BaseProvider):
    name = "openai"

    def is_configured(self) -> bool:
        return bool(config.OPENAI_API_KEY)

    def generate(self, system_prompt: str, messages: list[dict]) -> LLMResult:
        if not self.is_configured():
            return LLMResult(text="", error="OPENAI_API_KEY is not set (add it to .env).")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[{"role": "system", "content": system_prompt}, *messages],
                temperature=0.3,
                max_tokens=700,
            )
            text = resp.choices[0].message.content or ""
            return LLMResult(text=text, raw_model=config.OPENAI_MODEL)
        except Exception as e:
            return LLMResult(text="", error=f"OpenAI call failed: {e}")
