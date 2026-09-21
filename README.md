# Enterprise AI Assistant

A role-aware, multi-agent RAG assistant skeleton for enterprise knowledge bases — retrieval is scoped by role (RBAC), every query is audit-logged, and the agent pipeline (Planner -> Retriever -> Responder) is fully swappable for real LLM/embedding backends. Runs entirely offline by default (no external API keys required).

Overview · Architecture · RBAC · Quick Start · API Docs

## Overview

Most internal RAG assistants either expose everything to everyone or bolt access control on as an afterthought. This project treats RBAC as a first-class part of the retrieval path: a user's role determines which document categories they can retrieve and which tools the planner is allowed to invoke, enforced before any search happens — not filtered after the fact.

What this demonstrates:
- Role-scoped retrieval (admin / analyst / viewer) baked into the vector search itself
- A deterministic, swappable multi-agent pipeline (Planner -> Retriever -> Responder)
- Append-only audit logging of every query, retrieval, and tool-access decision
- Per-session conversation memory with a configurable window
- A config file (`config.yaml`) that documents every swap point for production (real embeddings, an LLM planner, Redis-backed memory)

## Architecture

```
  User Query --> PlannerAgent --> RetrieverAgent --> ResponderAgent --> Answer
                      |                 |                   |
                      v                 v                   v
                 plan steps      RBAC-filtered          synthesized
                 (rule-based)    VectorStore search      response
                      |                 |
                      +--------> AuditLog (audit.py) <---+
```

- **PlannerAgent** — keyword-driven step planner (retrieve, optionally call_api / run_computation, synthesize). Swap for an LLM-driven planner without touching the rest of the pipeline.
- **RetrieverAgent** — searches the in-process `VectorStore` (TF-IDF-style term vectors + cosine similarity), filtered to the caller's role via `rbac.py`.
- **ResponderAgent** — extractive synthesis from the top retrieved chunks. Swap for a generative LLM call in production.
- **RBAC** (`app/rbac.py`) — `admin` / `analyst` / `viewer` roles, each with a document-category allowlist and a tool allowlist. Denials are audit-logged.
- **Audit log** (`app/audit.py`) — every query, retrieval, and tool-access decision is appended as a JSON line to `audit.log`.
- **Conversation memory** (`app/memory.py`) — per-session sliding window (`collections.deque`), in-memory by default.

## RBAC

| Role | Document categories | Tools |
|---|---|---|
| `admin` | finance, hr, engineering, public | query_database, call_api, run_computation |
| `analyst` | finance, public | query_database |
| `viewer` | public | (none) |

Pass the caller's role via the `x-role` header; it defaults to `viewer` if omitted.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/cjoshi0209/Enterprise-Ai-Assistant
cd Enterprise-Ai-Assistant

# Environment
cp .env.example .env

# Docker (recommended)
docker-compose up -d

# Or local
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API is live at http://localhost:8000 · Docs at http://localhost:8000/docs

Run the test suite:

```bash
pip install -r requirements.txt
pytest -v
```

Bulk-ingest a folder of `.txt`/`.md` files:

```bash
python scripts/ingest.py --source ./docs/ --category public --api-url http://localhost:8000
```

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Service health check |
| `/roles` | GET | List configured roles and their permissions |
| `/ingest` | POST | Ingest a document into the vector store (admin only) |
| `/chat` | POST | Ask a question; returns an answer, sources, and the plan that was executed |
| `/chat/stream` | GET | Same as `/chat`, streamed via Server-Sent Events |

## Stack

Python 3.11 · FastAPI · pytest · Docker · pure-Python TF-IDF retrieval (no external embedding API required)

## Related

Built as part of the agent-infrastructure work at ORIXEN.AI — exploring how RBAC, observability, and swappable components fit into production multi-agent systems. If you're building something similar and want to compare notes, reach out on LinkedIn.

Built by Chinmay Joshi · ORIXEN.AI
