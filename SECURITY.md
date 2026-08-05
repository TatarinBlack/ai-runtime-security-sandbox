# Security Policy

This repository is an **intentionally vulnerable educational sandbox**, built
to demonstrate real prompt injection, data leakage, and excessive agency
techniques against a RAG chatbot in a conference talk.

## Please read before using

- **`Secure Mode = OFF` is deliberately unsafe.** The vulnerable code paths in
  `app/security/`, the poisoned documents in `data/documents/`, and the mock
  tool executions in `app/security/tools.py` exist on purpose, to be shown
  live. They are not bugs.
- **Do not deploy this application, or any part of it, to a public or
  production environment.** It has no authentication, no rate limiting, and
  (in Vulnerable Mode) no output filtering by design.
- **The mock tools never touch real systems.** `send_email()` and
  `delete_file()` only log a line to the Security Log / Tool Events panel —
  no email is sent, no file is deleted.
- **Run it locally only**, on `127.0.0.1`, for demo and learning purposes.

## Reporting a real vulnerability in this codebase

If you find a security issue in the *infrastructure* of this project itself
(e.g. something that would let Vulnerable Mode's behavior leak beyond
`127.0.0.1`, or a flaw in Protected Mode that shouldn't be there), please open
an issue or reach out directly rather than filing a public report — see the
contact details in [README.md](README.md).

Vulnerabilities that are *part of the intentional demo* (the eight scenarios
described in the README) are not bugs and don't need to be reported — that's
the point of the project.
