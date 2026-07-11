# AI Runtime Security Sandbox

**A fully local, self-contained RAG chatbot built to make Prompt Injection, Tool Abuse, Excessive Agency, Data Leakage, and Insecure Output Handling visible — live, in front of an audience.**

[![License: MIT](https://img.shields.io/badge/License-MIT-34e6d8.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](requirements.txt)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](app/main.py)
[![Status: Demo](https://img.shields.io/badge/Status-Educational%20Demo-ffb454.svg)](SECURITY.md)

> ⚠️ **This is an intentionally vulnerable educational sandbox.** It is built
> to demonstrate real attack techniques against a RAG chatbot, live, in a
> conference talk. Do not deploy it to a public or production environment.
> Full disclaimer in [SECURITY.md](SECURITY.md).

Six live attack scenarios, one click each, with a `Secure Mode` switch that
shows the exact same attack get blocked in real time — plus an in-app
Architecture view and an Attack Flow panel so an audience can follow along
without a single slide.

Built as the companion sandbox for the talk *"AI Runtime Security: Breaking
(and Defending) RAG Chatbots — Live"* (Azure OpenAI · RAG Agents · Process &
Culture track). Slides are in [`/slides`](slides/).

## Table of contents

- [Why this exists](#why-this-exists)
- [Quickstart](#quickstart)
- [Architecture](#architecture-short-version)
- [The 6 demo scenarios](#the-6-demo-scenarios)
- [Knowledge base](#knowledge-base)
- [Troubleshooting](#troubleshooting)
- [Slides](#slides)
- [License](#license)

## Why this exists

Traditional security controls protect networks, endpoints, identities, and
applications. RAG chatbots and AI agents open a new attack surface: prompts
become input, models become decision engines, agents execute actions, and
tools get direct access to business systems. This sandbox makes five of the
OWASP LLM Top 10 risk categories reproducible and demonstrable in minutes,
against your choice of Azure OpenAI, OpenAI, Anthropic Claude, Google Gemini,
or any local OpenAI-compatible model — with zero setup cost thanks to a
built-in offline mock model.

## Quickstart

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open **http://127.0.0.1:8000**. Select the `mock` provider on the left and
click any scenario card — no API key required, no internet required.

Fill in `.env` if you'd rather demo against a real model:

- **OpenAI**: `OPENAI_API_KEY`
- **Claude**: `ANTHROPIC_API_KEY`
- **Gemini**: `GOOGLE_API_KEY`
- **Custom**: `CUSTOM_BASE_URL` + `CUSTOM_API_KEY` — any OpenAI-compatible
  endpoint (Ollama, LM Studio, vLLM, Azure OpenAI, etc.)

The `mock` provider runs the whole system at 100% reliability with no
internet connection — the safest default for rehearsal and as a live
fallback if the venue Wi-Fi fails.

## Architecture (short version)

```
User message
  → [1] Input Guardrail (jailbreak pattern check on the raw message)
  → [2] RAG Retrieval (TF-IDF, top-3, offline)
  → [3] Retrieval Access Control (confidential chunks dropped in secure mode)
  → [4] Context Sanitization (instructions embedded in chunks are stripped)
  → [5] Instruction Hierarchy ("retrieved content is data, not commands")
  → [6] LLM call (OpenAI / Claude / Gemini / Custom / Mock)
  → [7] Output Guardrail / DLP (sensitive data patterns redacted)
  → [8] Output Link Guardrail (non-allowlisted markdown links/images stripped)
  → [9] Tool Authorization (tool calls sourced from untrusted content blocked)
  → Answer + Attack Flow + Retrieved Context + Security Log + Tool Events
```

With `Secure Mode` off, steps 1, 3, 4, 5, 7, 8, and 9 are disabled — this is
the intentionally vulnerable baseline. Click **⌗ System Architecture** in the
top bar to show this pipeline, the knowledge base contents, and the full
scenario → OWASP LLM Top 10 mapping table live, without leaving the app.

## The 6 demo scenarios

Every scenario card in the left panel pre-fills the attack prompt into the
chat box (no live typing, no typo risk) and — as soon as you click it — opens
the **Attack Flow** tab on the right, which shows for a general audience:

- exactly which document in the knowledge base is the attack vector, and its
  classification
- the attacker's-eye-view, step by step, of how the attack reaches the model
- what "PROTECTED" mode does differently, mechanically
- a presenter script (what to say, what to click)

| # | Scenario | OWASP LLM Top 10 | Target document |
|---|---|---|---|
| 1 | Indirect Prompt Injection | LLM01 (Indirect) | `vendor_terms_poisoned.md` |
| 2 | Data Leakage | LLM06 | `confidential_salaries.md` |
| 3 | Excessive Agency — Tool Abuse (exfiltration) | LLM08 | `support_ticket_with_tool_injection.md` |
| 4 | Direct Jailbreak | LLM01 (Direct) | none — the user is the attacker |
| 5 | Insecure Output Handling — Markdown Exfiltration | LLM02 | `marketing_newsletter_poisoned.md` |
| 6 | Excessive Agency — Destructive Tool Call | LLM08 | `it_maintenance_request_poisoned.md` |

Suggested rhythm for each one, live: **click the card → send with Secure Mode
OFF (attack succeeds) → flip Secure Mode ON → send the exact same message
again (attack is blocked) → point at the Security Log tab.**

With `mock` selected, everything is 100% deterministic and works offline. A
real provider (OpenAI/Claude/Gemini/Azure OpenAI) behaves more "realistically"
but less predictably — that difference is itself worth calling out live.

## Knowledge base

`data/documents/*.md` — each file starts with a small frontmatter block:

```
---
classification: public | internal | confidential
scenario: general | injection | leakage | agency | exfiltration | destructive_agency
---
```

Edit or add documents, then refresh the page (the index reloads automatically
on server start; call `POST /api/documents/reload` to refresh without
restarting).

## Troubleshooting

- **"No API key is configured"**: `.env` wasn't filled in, or the server
  wasn't restarted after editing it. `mock` always works regardless.
- **`pip install` fails building `pydantic-core`**: your Python/platform
  doesn't have a prebuilt wheel for the pinned version. `requirements.txt`
  intentionally avoids hard version pins for this reason — run
  `pip install --upgrade pip` and try again.
- **A scenario doesn't behave as expected**: use the scenario cards, not
  free-typed questions — TF-IDF retrieval is tuned against the exact prompt
  wording in each card.
- **Port 8000 busy**: change `APP_PORT` in `.env`.

## Slides

[`/slides/AI-Runtime-Security-RAG-Chatbot-Talk.pptx`](slides/) — the
companion deck for the live talk: problem framing, the Azure OpenAI RAG Agent
reference architecture, the 4 primary scenarios as presenter cue cards, the
sandbox → Azure AI Agent design-pattern mapping, and governance takeaways.
Speaker notes are embedded per slide.

## Contributing

This is a talk companion project, not an actively maintained framework — but
issues and PRs for bugs, new scenarios, or additional provider support are
welcome.

## License

MIT — see [LICENSE](LICENSE). See [SECURITY.md](SECURITY.md) before using or
deploying this project anywhere beyond your own machine.
