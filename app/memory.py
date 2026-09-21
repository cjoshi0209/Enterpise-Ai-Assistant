"""Session-scoped conversation memory with a configurable history window."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque, Dict, List, Tuple


class ConversationMemory:
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self._sessions: Dict[str, Deque[Tuple[str, str]]] = defaultdict(
            lambda: deque(maxlen=self.window_size)
        )

    def add(self, session_id: str, role: str, content: str) -> None:
        self._sessions[session_id].append((role, content))

    def get(self, session_id: str) -> List[Tuple[str, str]]:
        return list(self._sessions[session_id])

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
