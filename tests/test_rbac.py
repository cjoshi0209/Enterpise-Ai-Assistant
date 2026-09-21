import pytest

from app.rbac import AccessDeniedError, check_tool_access, filter_documents_for_role


def test_viewer_only_sees_public_docs():
    docs = [
        {"category": "public", "text": "a"},
        {"category": "finance", "text": "b"},
    ]
    filtered = filter_documents_for_role("viewer", docs)
    assert len(filtered) == 1
    assert filtered[0]["category"] == "public"


def test_admin_sees_everything():
    docs = [
        {"category": "public", "text": "a"},
        {"category": "finance", "text": "b"},
        {"category": "hr", "text": "c"},
    ]
    assert len(filter_documents_for_role("admin", docs)) == 3


def test_viewer_cannot_call_tools():
    with pytest.raises(AccessDeniedError):
        check_tool_access("viewer", "query_database")


def test_analyst_can_query_database():
    check_tool_access("analyst", "query_database")  # should not raise
