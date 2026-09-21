"""Multi-agent orchestration: Planner -> Retriever -> Responder.

Each agent has a single, clearly-scoped responsibility, matching the
architecture diagram in the README. The orchestrator wires them together and
enforces RBAC before any retrieval happens.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from app.audit import log_event
from app.rbac import check_tool_access, get_role
from app.vector_store import VectorStore


@dataclass
class AgentResponse:
    answer: str
    sources: List[dict]
    plan: List[str]


class PlannerAgent:
    """Breaks a user request into retrieval + tool sub-steps.

    Deliberately simple/deterministic (keyword-driven) so the whole pipeline
    runs without a paid LLM call; swap `plan()` for an LLM-driven planner in
    production without touching the rest of the orchestrator.
    """

    def plan(self, query: str) -> List[str]:
        steps = ["retrieve_context"]
        lowered = query.lower()
        if any(kw in lowered for kw in ("calculate", "compute", "sum", "average")):
            steps.append("run_computation")
        if any(kw in lowered for kw in ("latest", "current", "lookup", "check")):
            steps.append("call_api")
        steps.append("synthesize_response")
        return steps


class RetrieverAgent:
    def __init__(self, store: VectorStore):
        self.store = store

    def retrieve(self, query: str, role_name: str, top_k: int = 5) -> List[dict]:
        role = get_role(role_name)
        return self.store.search(query, top_k=top_k, allowed_categories=role.document_categories)


class ResponderAgent:
    def synthesize(self, query: str, retrieved: List[dict]) -> str:
        if not retrieved:
            return (
                "I couldn't find anything in the documents you're authorized to see "
                "that answers that. Try rephrasing, or ask an admin for access to the "
                "relevant category."
            )
        top = retrieved[0]
        supporting = "; ".join(r["text"][:160] for r in retrieved[:3])
        return f"Based on {top['source']}: {supporting}"


class AgentOrchestrator:
    def __init__(self, store: Optional[VectorStore] = None):
        self.store = store or VectorStore()
        self.planner = PlannerAgent()
        self.retriever = RetrieverAgent(self.store)
        self.responder = ResponderAgent()

    def handle(self, query: str, role_name: str, session_id: str = "default") -> AgentResponse:
        plan = self.planner.plan(query)
        log_event("query", role=role_name, session_id=session_id, query=query, plan=plan)

        for step in plan:
            if step in ("run_computation", "call_api"):
                try:
                    check_tool_access(role_name, step)
                except PermissionError:
                    log_event("tool_denied", role=role_name, tool=step)
                    plan = [s for s in plan if s != step]

        retrieved = self.retriever.retrieve(query, role_name)
        log_event("retrieval", role=role_name, session_id=session_id, hits=len(retrieved))

        answer = self.responder.synthesize(query, retrieved)
        return AgentResponse(answer=answer, sources=retrieved, plan=plan)
