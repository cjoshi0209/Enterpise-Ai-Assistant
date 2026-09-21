"""Minimal in-process vector store.

Uses TF-IDF-style term vectors and cosine similarity so the whole assistant
runs without any external embedding API. Swap `embed()` for a real embedding
model (OpenAI, sentence-transformers, etc.) in production -- the storage and
search interface stays the same.
"""
from __future__ import annotations

import math
import re
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


@dataclass
class Chunk:
    id: str
    text: str
    category: str
    source: str
    vector: Counter = field(default_factory=Counter)


def chunk_text(text: str, chunk_size: int = 512) -> List[str]:
    words = text.split()
    return [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)] or [text]


class VectorStore:
    def __init__(self):
        self._chunks: Dict[str, Chunk] = {}
        self._doc_freq: Counter = Counter()

    def _vectorize(self, text: str) -> Counter:
        return Counter(_tokenize(text))

    def ingest(self, text: str, category: str = "public", source: str = "unknown", chunk_size: int = 512) -> List[str]:
        ids = []
        for piece in chunk_text(text, chunk_size=chunk_size):
            chunk_id = str(uuid.uuid4())
            vec = self._vectorize(piece)
            self._chunks[chunk_id] = Chunk(id=chunk_id, text=piece, category=category, source=source, vector=vec)
            for term in vec:
                self._doc_freq[term] += 1
            ids.append(chunk_id)
        return ids

    def _similarity(self, a: Counter, b: Counter) -> float:
        if not a or not b:
            return 0.0
        shared = set(a) & set(b)
        dot = sum(a[t] * b[t] for t in shared)
        norm_a = math.sqrt(sum(v * v for v in a.values()))
        norm_b = math.sqrt(sum(v * v for v in b.values()))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

    def search(self, query: str, top_k: int = 5, allowed_categories: Optional[set] = None) -> List[dict]:
        query_vec = self._vectorize(query)
        scored = []
        for chunk in self._chunks.values():
            if allowed_categories is not None and chunk.category not in allowed_categories:
                continue
            score = self._similarity(query_vec, chunk.vector)
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"id": c.id, "text": c.text, "category": c.category, "source": c.source, "score": round(s, 4)}
            for s, c in scored[:top_k]
        ]

    def __len__(self) -> int:
        return len(self._chunks)
