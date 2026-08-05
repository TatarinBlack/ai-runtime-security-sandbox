# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.2.0] — 2026-08-05

### Added

- **8th scenario: Memory Poisoning (Persistent Memory Injection)** — a
  hidden directive planted inside an auto-summarized entry in the agent's
  own persistent memory log (not a business document, not a tool manifest)
  resurfaces and hijacks a completely unrelated later session. Maps to
  **ASI06: Memory & Context Poisoning**. New document:
  `data/documents/agent_memory_log_poisoned.md`. Reuses the existing
  retrieval + Context Sanitization + Tool Authorization pipeline unchanged.
- **Hardening Scorecard** (`🛡 Hardening Score` in the top bar, `GET
  /api/scorecard`) — replays every scenario's default prompt through the
  full pipeline in both modes against the deterministic `mock` provider and
  grades each one `neutralized` / `succeeded`, rolling the result up into a
  single pass/fail score. The same check a CI/CD gate would run before
  shipping a guardrail change. Backend pipeline logic in `app/main.py` was
  extracted into a reusable `run_pipeline()` function shared by `/api/chat`
  and `/api/scorecard`.
- **Obfuscation-aware guardrails** — the Input Guardrail and Context
  Sanitization now also decode Base64 and ROT13 before pattern-matching
  (`guardrails.try_decode_obfuscations()`), closing a real evasion
  technique where an attacker encodes a plaintext-matched instruction to
  slip past a keyword/regex filter. A `Plain / 🌀 Base64 / 🌀 ROT13`
  dropdown next to the chat Send button lets you encode any message
  (including a scenario's pre-filled prompt) before sending, to test the
  bypass live. Security Log entries caught this way are tagged `[decoded
  from obfuscated payload]`.

## [1.1.0] — 2026-07-22

### Added

- **7th scenario: MCP Tool Poisoning (Rug Pull)** — a hidden directive
  embedded in an MCP tool's own description (not in a business document)
  silently triggers a tool call the moment the agent enumerates its tools.
  New document: `data/documents/mcp_tool_registry_poisoned.md`.
- Mapping to the newly published **OWASP Top 10 for Agentic Applications
  (2026)** (ASI01–ASI10) alongside the existing OWASP LLM Top 10 mapping,
  shown in the in-app Architecture view and the README scenario table.
- "Real-world context" section in the README referencing EchoLeak
  (Microsoft 365 Copilot zero-click prompt injection, June 2025) and the
  broader 2025–2026 rise of MCP tool-poisoning attacks.
- DefansX branding in the app header (logo + refreshed button/card styling
  across the UI, tied to the brand's cyan-to-blue palette).
- `CONTRIBUTING.md`, this `CHANGELOG.md`, and a "Related projects" section
  in the README.

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
