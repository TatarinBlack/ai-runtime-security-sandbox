"""
Central configuration. Reads from .env, falls back to safe defaults if absent.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DOCS_DIR = BASE_DIR / "data" / "documents"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

CUSTOM_BASE_URL = os.getenv("CUSTOM_BASE_URL", "http://localhost:11434/v1")
CUSTOM_API_KEY = os.getenv("CUSTOM_API_KEY", "ollama")
CUSTOM_MODEL = os.getenv("CUSTOM_MODEL", "llama3.1")

APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# Retrieval settings
TOP_K = 3
# Chunks scoring below this threshold are never included in the context.
# Purpose: for off-topic queries (e.g. a direct jailbreak attempt) the RAG
# retriever should return nothing rather than leaking random low-score noise
# into the prompt and muddying the scenario.
MIN_SCORE = 0.15
