from app.agents import AgentOrchestrator


def test_viewer_only_retrieves_public_chunks():
    orch = AgentOrchestrator()
    orch.store.ingest("The office WiFi password is posted in the lobby.", category="public", source="handbook")
    orch.store.ingest("Q3 revenue was $4.2M, up 12% YoY.", category="finance", source="finance-deck")

    result = orch.handle("What was revenue?", role_name="viewer")
    assert all(s["category"] == "public" for s in result.sources)


def test_analyst_can_retrieve_finance_docs():
    orch = AgentOrchestrator()
    orch.store.ingest("Q3 revenue was $4.2M, up 12% YoY.", category="finance", source="finance-deck")

    result = orch.handle("What was Q3 revenue?", role_name="analyst")
    assert any(s["category"] == "finance" for s in result.sources)


def test_no_matching_documents_gives_graceful_answer():
    orch = AgentOrchestrator()
    result = orch.handle("anything", role_name="viewer")
    assert "couldn't find" in result.answer
