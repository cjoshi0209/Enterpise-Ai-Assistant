"""Role-based access control.

Roles map to (a) which document categories they can retrieve and (b) which
tools they're allowed to invoke. Kept as a plain in-memory policy so it's
trivial to swap for a real IdP/policy engine later.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet


class AccessDeniedError(PermissionError):
    pass


@dataclass(frozen=True)
class Role:
    name: str
    document_categories: FrozenSet[str]
    tools: FrozenSet[str]


ROLES: Dict[str, Role] = {
    "admin": Role(
        name="admin",
        document_categories=frozenset({"finance", "hr", "engineering", "public"}),
        tools=frozenset({"query_database", "call_api", "run_computation"}),
    ),
    "analyst": Role(
        name="analyst",
        document_categories=frozenset({"finance", "public"}),
        tools=frozenset({"query_database"}),
    ),
    "viewer": Role(
        name="viewer",
        document_categories=frozenset({"public"}),
        tools=frozenset(),
    ),
}


def get_role(role_name: str) -> Role:
    try:
        return ROLES[role_name]
    except KeyError as exc:
        raise AccessDeniedError(f"Unknown role: {role_name}") from exc


def filter_documents_for_role(role_name: str, documents: list[dict]) -> list[dict]:
    role = get_role(role_name)
    return [d for d in documents if d.get("category", "public") in role.document_categories]


def check_tool_access(role_name: str, tool: str) -> None:
    role = get_role(role_name)
    if tool not in role.tools:
        raise AccessDeniedError(f"Role '{role_name}' is not permitted to call tool '{tool}'")
