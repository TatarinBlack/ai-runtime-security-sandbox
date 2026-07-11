from .base import BaseProvider, LLMResult
from app import config


class GeminiProvider(BaseProvider):
    name = "gemini"

    def is_configured(self) -> bool:
        return bool(config.GOOGLE_API_KEY)

    def generate(self, system_prompt: str, messages: list[dict]) -> LLMResult:
        if not self.is_configured():
            return LLMResult(text="", error="GOOGLE_API_KEY is not set (add it to .env).")
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.GOOGLE_API_KEY)
            model = genai.GenerativeModel(config.GEMINI_MODEL, system_instruction=system_prompt)
            # Gemini simple single-turn chat: flatten history into one text block.
            convo = []
            for m in messages[:-1]:
                prefix = "User" if m["role"] == "user" else "Assistant"
                convo.append(f"{prefix}: {m['content']}")
            last_user = messages[-1]["content"] if messages else ""
            prompt = "\n".join(convo + [f"User: {last_user}"]) if convo else last_user
            resp = model.generate_content(prompt)
            return LLMResult(text=resp.text or "", raw_model=config.GEMINI_MODEL)
        except Exception as e:
            return LLMResult(text="", error=f"Gemini call failed: {e}")
