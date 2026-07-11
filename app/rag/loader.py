"""
Reads .md files from the data/documents folder.
Each file may optionally start with a YAML-like frontmatter block:

---
classification: confidential
scenario: leakage
---
body text...

classification: public | internal | confidential  -> used for access control in secure mode
scenario: which demo scenario this source belongs to (UI labeling only)
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from app import config

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


@dataclass
class Document:
    filename: str
    classification: str
    scenario: str
    body: str


@dataclass
class Chunk:
    doc_filename: str
    classification: str
    scenario: str
    chunk_id: str
    text: str


def _parse_file(path: Path) -> Document:
    raw = path.read_text(encoding="utf-8")
    meta = {"classification": "public", "scenario": "general"}
    body = raw
    m = FRONTMATTER_RE.match(raw)
    if m:
        fm_block, body = m.group(1), m.group(2)
        for line in fm_block.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return Document(filename=path.name, classification=meta.get("classification", "public"),
                     scenario=meta.get("scenario", "general"), body=body.strip())


def load_documents() -> list[Document]:
    config.DOCS_DIR.mkdir(parents=True, exist_ok=True)
    docs = []
    for path in sorted(config.DOCS_DIR.glob("*.md")):
        docs.append(_parse_file(path))
    return docs


def chunk_documents(docs: list[Document]) -> list[Chunk]:
    chunks = []
    for doc in docs:
        paragraphs = [p.strip() for p in doc.body.split("\n\n") if len(p.strip()) > 15]
        if not paragraphs:
            paragraphs = [doc.body.strip()] if doc.body.strip() else []
        for i, p in enumerate(paragraphs):
            chunks.append(Chunk(
                doc_filename=doc.filename,
                classification=doc.classification,
                scenario=doc.scenario,
                chunk_id=f"{doc.filename}#{i}",
                text=p,
            ))
    return chunks
