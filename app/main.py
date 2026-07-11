from pathlib import Path
from typing import List, Dict, Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import config
from app.providers import get_provider, list_providers
from app.rag.retriever import retriever
from app.security import guardrails, tools
from app.security.scenarios import SCENARIOS, KNOWLEDGE_BASE

APP_DIR = Path(__file__).resolve().parent

app = FastAPI(title="AI Runtime Security Sandbox")
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


class ChatRequest(BaseModel):
    message: str
    provider: str = "mock"
    secure_mode: bool = False
    history: List[Dict[str, str]] = Field(default_factory=list)


@app.get("/")
def index():
    return FileResponse(str(APP_DIR / "static" / "index.html"))


@app.get("/api/providers")
def api_providers():
    return list_providers()


@app.get("/api/scenarios")
def api_scenarios():
    return SCENARIOS


@app.get("/api/knowledge-base")
def api_knowledge_base():
    return {**KNOWLEDGE_BASE, "documents": retriever.list_documents_meta()}


@app.get("/api/documents")
def api_documents():
    return retriever.list_documents_meta()


@app.post("/api/documents/reload")
def api_documents_reload():
    retriever.reload()
    return {"status": "ok", "documents": retriever.list_documents_meta()}


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    secure_mode = req.secure_mode
    security_log: list[dict] = []

    provider = get_provider(req.provider)
    if not provider.is_configured():
        return {
            "answer": f"⚠️ No API key is configured for provider '{req.provider}'. "
                      f"Fill in .env or try the 'mock' provider instead.",
            "retrieved_chunks": [], "tool_events": [], "security_log": [],
            "secure_mode": secure_mode, "provider": req.provider, "blocked": False,
        }

    # 1) INPUT GUARDRAIL: does the user's own message contain a direct jailbreak pattern?
    jb_matches = guardrails.detect_jailbreak(req.message)
    if secure_mode and jb_matches:
        security_log.append({
            "stage": "input_guardrail", "severity": "blocked",
            "message": f"The user message matched a known instruction-override pattern "
                       f"({jb_matches[0]}). The request was rejected before ever reaching the model.",
        })
        return {
            "answer": "I can't help with that: your message matched a pattern for changing or "
                      "revealing system instructions. How can I help you with information from the "
                      "documents instead?",
            "retrieved_chunks": [], "tool_events": [], "security_log": security_log,
            "secure_mode": secure_mode, "provider": req.provider, "blocked": True,
        }

    # 2) RETRIEVAL + ACCESS CONTROL
    raw_chunks = retriever.retrieve(req.message, top_k=config.TOP_K)
    filtered_chunks = guardrails.filter_by_classification(raw_chunks, secure_mode)
    if secure_mode and len(filtered_chunks) < len(raw_chunks):
        removed_docs = [c["doc"] for c in raw_chunks if c not in filtered_chunks]
        security_log.append({
            "stage": "retrieval_access_control", "severity": "blocked",
            "message": f"{len(raw_chunks) - len(filtered_chunks)} confidential chunk(s) were excluded "
                       f"from the context: {', '.join(removed_docs)}",
        })

    # 3) CONTEXT SANITIZATION (indirect injection cleanup)
    sanitized = guardrails.sanitize_chunks(filtered_chunks, secure_mode)
    for c in sanitized:
        if c["injection_detected"]:
            security_log.append({
                "stage": "context_sanitization",
                "severity": "sanitized" if secure_mode else "not_blocked",
                "message": f"An injection pattern was detected inside {c['doc']} "
                           f"({', '.join(c['matched_patterns'])}). " +
                           ("The offending sentence was stripped from the context before the model saw it."
                            if secure_mode else
                            "secure mode is OFF — the model will see this instruction as-is."),
            })

    context_block = "\n\n".join(f"[{c['doc']}] {c['safe_text']}" for c in sanitized) \
        if sanitized else "(No relevant document found)"

    # 4) INSTRUCTION HIERARCHY / PROMPT HARDENING
    system_prompt = guardrails.build_system_prompt(secure_mode, context_block)

    # 5) LLM CALL
    messages = [*req.history, {"role": "user", "content": req.message}]
    result = provider.generate(system_prompt, messages)
    if result.error:
        security_log.append({"stage": "provider", "severity": "error", "message": result.error})
        return {
            "answer": f"⚠️ {result.error}", "retrieved_chunks": sanitized, "tool_events": [],
            "security_log": security_log, "secure_mode": secure_mode,
            "provider": req.provider, "blocked": False,
        }

    answer_text = result.text

    # 6) OUTPUT GUARDRAIL (DLP)
    clean_answer, dlp_findings = guardrails.dlp_scan(answer_text, secure_mode)
    if dlp_findings:
        security_log.append({
            "stage": "output_dlp",
            "severity": "redacted" if secure_mode else "leaked",
            "message": f"Sensitive data pattern(s) detected in the answer: {', '.join(dlp_findings)}."
                       + ("" if secure_mode else " secure mode is OFF — no redaction was applied."),
        })

    # 7) OUTPUT LINK GUARDRAIL (blocks markdown/image exfiltration)
    clean_answer, link_findings = guardrails.sanitize_output_links(clean_answer, secure_mode)
    if link_findings:
        security_log.append({
            "stage": "output_link_guardrail",
            "severity": "blocked" if secure_mode else "leaked",
            "message": f"Markdown link/image pointing at non-allowlisted domain(s) detected: "
                       f"{', '.join(link_findings)}."
                       + ("" if secure_mode else " secure mode is OFF — the link was left in the answer."),
        })

    # 8) TOOL AUTHORIZATION (excessive agency / tool abuse prevention)
    context_had_injection = any(c["injection_detected"] for c in sanitized)
    tool_events = []
    for call in tools.parse_tool_calls(answer_text):
        source = "retrieved_content" if context_had_injection else "user_explicit"
        allowed, reason = guardrails.authorize_tool_call(source, secure_mode)
        if allowed:
            exec_result = tools.execute_mock_tool(call["tool"], call["args"])
            tool_events.append({**call, "status": "executed", "result": exec_result, "source": source})
            security_log.append({
                "stage": "tool_authorization", "severity": "executed",
                "message": f"{call['tool']}() was executed (source: {source}).",
            })
        else:
            tool_events.append({**call, "status": "blocked", "result": reason, "source": source})
            security_log.append({"stage": "tool_authorization", "severity": "blocked", "message": reason})
            clean_answer = tools.TOOL_CALL_RE.sub("[TOOL CALL BLOCKED]", clean_answer)

    return {
        "answer": clean_answer,
        "retrieved_chunks": sanitized,
        "tool_events": tool_events,
        "security_log": security_log,
        "secure_mode": secure_mode,
        "provider": req.provider,
        "blocked": False,
    }
