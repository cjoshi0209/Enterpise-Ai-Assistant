from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200


def test_ingest_requires_admin():
    with TestClient(app) as client:
        resp = client.post(
            "/ingest",
            json={"text": "some doc", "category": "public"},
            headers={"x-role": "viewer"},
        )
        assert resp.status_code == 403


def test_admin_ingest_then_chat():
    with TestClient(app) as client:
        ingest_resp = client.post(
            "/ingest",
            json={"text": "Refunds are processed within 30 days.", "category": "public", "source": "policy"},
            headers={"x-role": "admin"},
        )
        assert ingest_resp.status_code == 200

        chat_resp = client.post(
            "/chat",
            json={"query": "How do refunds work?", "session_id": "s1"},
            headers={"x-role": "viewer"},
        )
        assert chat_resp.status_code == 200
        assert "answer" in chat_resp.json()
