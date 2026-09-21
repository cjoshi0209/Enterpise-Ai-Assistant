from __future__ import annotations

import asyncio
import json
from typing import List, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents import AgentOrchestrator
from app.memory import ConversationMemory
from app.rbac import AccessDeniedError, ROLES

app = FastAPI(
    title="Enterprise AI Assistant",
    description="Multi-agent enterprise assistant with RAG backend, tool-use "
    "orchestration, and role-based access control.",
    version="0.1.0",
)

orchestrator = AgentOrchestrator()
memory = ConversationMemory(window_size=10)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    session_id: str = "default"


class IngestRequest(BaseModel):
    text: str = Field(..., min_length=1)
    category: str = "public"
    source: str = "manual-upload"


def _require_role(x_role: Optional[str]) -> str:
    role = x_role or "viewer"
    if role not in ROLES:
        raise HTTPException(status_code=403, detail=f"Unknown role '{role}'")
    return role


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/roles")
def roles() -> dict:
    return {
        name: {
            "document_categories": sorted(role.document_categories),
            "tools": sorted(role.tools),
        }
        for name, role in ROLES.items()
    }


@app.post("/ingest")
def ingest(req: IngestRequest, x_role: Optional[str] = Header(default=None)) -> dict:
    role = _require_role(x_role)
    if role not in ("admin",):
        raise HTTPException(status_code=403, detail="Only admin may ingest documents")
    ids = orchestrator.store.ingest(req.text, category=req.category, source=req.source)
    return {"chunks_ingested": len(ids), "chunk_ids": ids}


@app.post("/chat")
def chat(req: ChatRequest, x_role: Optional[str] = Header(default=None)) -> dict:
    role = _require_role(x_role)
    memory.add(req.session_id, "user", req.query)
    try:
        result = orchestrator.handle(req.query, role, session_id=req.session_id)
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    memory.add(req.session_id, "assistant", result.answer)
    return {
        "answer": result.answer,
        "sources": result.sources,
        "plan": result.plan,
        "history_length": len(memory.get(req.session_id)),
    }


@app.get("/chat/stream")
async def chat_stream(query: str, session_id: str = "default", x_role: Optional[str] = Header(default=None)):
    role = _require_role(x_role)

    async def event_source():
        result = orchestrator.handle(query, role, session_id=session_id)
        for word in result.answer.split(" "):
            yield f"data: {json.dumps({'token': word})}\n\n"
            await asyncio.sleep(0.02)
        yield f"data: {json.dumps({'done': True, 'sources': result.sources})}\n\n"

    return StreamingResponse(event_source(), media_type="text/event-stream")
