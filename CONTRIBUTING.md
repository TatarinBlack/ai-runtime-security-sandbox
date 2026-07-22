# Contributing

Thanks for taking a look at this project. It started as a conference talk
companion, but it's meant to be useful (and safe to poke at) beyond that
single talk. Small, focused PRs are the easiest to review and merge.

Before anything else, read [SECURITY.md](SECURITY.md) — the vulnerable code
paths and poisoned documents in this repo are intentional, not bugs.

## Ways to contribute

- **Fix a bug** in the guardrail pipeline, retrieval tuning, or UI.
- **Add a new attack scenario** (see below) — the six existing scenarios are
  not meant to be an exhaustive list of the OWASP LLM Top 10.
- **Add a new provider** under `app/providers/` (anything OpenAI-compatible
  is usually a small diff on top of `custom_provider.py`).
- **Improve docs** — the README, SECURITY.md, or in-app Architecture/Attack
  Flow copy.

## Adding a new attack scenario

1. Add a poisoned or sensitive document to `data/documents/`, with a
   frontmatter block:
   ```
   ---
   classification: public | internal | confidential
   scenario: <your-scenario-id>
   ---
   ```
2. Register the scenario in `app/security/scenarios.py`: id, title, subtitle,
   attack prompt, `threat_tags`, `owasp` mapping, `target_doc`,
   `demonstrates`, `mechanism`, `attack_flow` steps, and presenter `narration`.
3. If the attack needs a new detection pattern (e.g. a new tool-abuse
   payload), add a trigger to `INJECTION_TRIGGERS` in
   `app/providers/mock_provider.py` — keep the match scoped to the retrieved
   context, never the full system prompt, to avoid false positives.
4. Test both modes: `Secure Mode OFF` should let the attack succeed,
   `Secure Mode ON` should block or sanitize it, and the Security Log should
   show why.
5. Tune retrieval — run the scenario prompt against `data/documents/` and
   confirm the target document is retrieved above `MIN_SCORE`
   (`app/config.py`) without pulling in an unrelated scenario's document.

## Code style

- Keep the mock provider deterministic — no randomness, no network calls.
  It's the reliability fallback for a live demo.
- Prefer explicit, named guardrail steps over combined logic — the pipeline
  is meant to be readable in a live walkthrough, not just correct.
- Frontend stays vanilla HTML/CSS/JS (no build step) so the UI keeps working
  offline with zero setup.

## Pull requests

1. Fork, branch off `main`.
2. Keep the PR scoped to one change (one scenario, one fix, one doc update).
3. Describe what you tested and how (which scenario, which mode, which
   provider).
4. Open the PR — no CLA, no fixed release cadence, but expect a review
   before merge.

## Reporting issues

Bug in the app itself → open a GitHub issue with repro steps.
Found something wrong with a *demo scenario's* behavior → check
[SECURITY.md](SECURITY.md) first, since some of what looks like a bug is the
intended vulnerability.
