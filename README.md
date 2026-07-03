<div align="center">

# Enterprise AI Assistant

**Multi-agent enterprise assistant with RAG backend, tool-use orchestration, and role-based access control — built for real deployment.**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.1-1C3C3C?style=flat-square)](https://langchain.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-7C3AED?style=flat-square)](LICENSE)

[Overview](#-overview) · [Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start)

</div>

---

## Overview

A production-ready enterprise AI assistant that goes beyond simple chatbots. It uses a **multi-agent architecture** where specialized agents handle retrieval, tool execution, and response synthesis — with full RBAC so different user roles see only what they're authorized for.

This isn't a demo. It's structured the way you'd actually deploy an AI assistant inside a company.

---

## Features

- **Multi-agent orchestration** — Planner, Retriever, and Responder agents with clear separation of concerns
- **RAG backend** — Document ingestion pipeline with chunking, embedding, and vector search
- **Tool-use** — Agents can call external APIs, query databases, and run computations
- **Role-Based Access Control** — Fine-grained permissions: what documents each role can retrieve, which tools they can invoke
- **Conversation memory** — Session-scoped memory with configurable history window
- **Streaming responses** — SSE-based streaming for real-time UX
- **Audit logging** — Every query, retrieval, and tool call is logged for compliance

---

## Architecture

```
User Request
      │
      ▼
 ┌──────────┐      ┌─────────────────────────────────┐
 │  Auth &  │      │         Agent Orchestrator       │
 │   RBAC   │─────►│                                  │
 └──────────┘      │  ┌──────────┐  ┌─────────────┐  │
                   │  │ Planner  │  │  Retriever  │  │
                   │  │  Agent   │  │    Agent    │  │
                   │  └──────────┘  └─────────────┘  │
                   │        │              │           │
                   │        ▼              ▼           │
                   │  ┌───────────────────────────┐   │
                   │  │      Responder Agent       │   │
                   │  └───────────────────────────┘   │
                   └─────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              Vector DB      Tool APIs     Audit Log
```

---

## Quick Start

```bash
git clone https://github.com/cjoshi0209/Enterpise-Ai-Assistant
cd Enterpise-Ai-Assistant

cp .env.example .env
# Configure OPENAI_API_KEY, DATABASE_URL, VECTOR_DB_URL

docker-compose up -d

# Ingest documents
python scripts/ingest.py --source ./docs/

# Start server
uvicorn app.main:app --reload
```

---

## Configuration

```yaml
# config.yaml
agents:
  planner: gpt-4
  retriever: text-embedding-ada-002
  responder: gpt-4

retrieval:
  top_k: 5
  similarity_threshold: 0.75
  chunk_size: 512

memory:
  window_size: 10
  backend: redis

rbac:
  roles: [admin, analyst, viewer]
```

---

## Stack

`Python 3.11` · `LangChain` · `OpenAI GPT-4` · `FastAPI` · `PostgreSQL` · `pgvector` · `Redis` · `Docker`

---

<div align="center">
Built by <a href="https://joshichinmay.tech">Chinmay Joshi</a> · <a href="https://orixenai.in">ORIXEN.AI</a>
</div>
