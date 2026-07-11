"""
Fake (mock) tools wired to the agent. Nothing here actually sends an email or
deletes a file — it only logs "if this were a real agent, this action would
really happen now", which is the entire point of the Excessive Agency / Tool
Abuse demos.
"""
import re
from datetime import datetime

TOOL_CALL_RE = re.compile(r"(send_email|delete_file|read_file)\(([^)]*)\)")

DESTRUCTIVE_TOOLS = {"delete_file"}


def parse_tool_calls(text: str) -> list[dict]:
    calls = []
    for m in TOOL_CALL_RE.finditer(text):
        calls.append({"tool": m.group(1), "args": m.group(2).strip()})
    return calls


def execute_mock_tool(tool: str, args: str) -> str:
    ts = datetime.now().strftime("%H:%M:%S")
    if tool == "send_email":
        return f"[{ts}] MOCK EXECUTION: email sent -> {args}"
    if tool == "delete_file":
        return f"[{ts}] MOCK EXECUTION: file deleted -> {args}"
    if tool == "read_file":
        return f"[{ts}] MOCK EXECUTION: file read -> {args}"
    return f"[{ts}] Unknown tool: {tool}"
