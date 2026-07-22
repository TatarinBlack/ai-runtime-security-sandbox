# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] — 2026-07-09

Initial public release.

### Added

- FastAPI backend with a provider-agnostic architecture: OpenAI, Anthropic
  Claude, Google Gemini, any OpenAI-compatible custom endpoint, and a fully
  offline deterministic mock provider.
- Local RAG pipeline over `data/documents/*.md` using offline TF-IDF
  retrieval (no embeddings API, no vector DB — runs with zero setup).
- Nine-step AI runtime security guardrail pipeline: input guardrail,
  retrieval access control, context sanitization, instruction hierarchy,
  output DLP, output link guardrail, and provenance-based tool authorization.
- Six live attack scenarios mapped to the OWASP LLM Top 10: Indirect Prompt
  Injection, Data Leakage, Excessive Agency (tool abuse / exfiltration),
  Direct Jailbreak, Insecure Output Handling (markdown exfiltration), and
  Excessive Agency (destructive tool call).
- Custom dark "security console" web UI with a `Secure Mode` toggle, an
  in-app System Architecture view, and a per-scenario Attack Flow panel that
  narrates the attacker's-eye-view path through the pipeline.
- Per-message Secure Mode badges and attack-verdict badges in chat history,
  so past messages remain unambiguous when switching modes mid-session.
- Companion slide deck (`slides/`) for the live talk, including an Azure
  OpenAI RAG Agent reference architecture and an OWASP LLM Top 10 recap.

### Notes

This is an intentionally vulnerable educational sandbox — see
[SECURITY.md](SECURITY.md) before deploying it anywhere beyond your own
machine.

[1.0.0]: https://github.com/TatarinBlack/ai-runtime-security-sandbox/releases/tag/v1.0.0
