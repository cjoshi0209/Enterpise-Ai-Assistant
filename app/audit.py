"""Append-only audit log. Every query, retrieval, and tool call is recorded
for compliance, as documented in the README.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Dict

AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "./audit.log")


def log_event(event_type: str, **fields: Any) -> Dict[str, Any]:
    record = {"ts": time.time(), "event": event_type, **fields}
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
    return record
