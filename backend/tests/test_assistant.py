import pytest
from app.main import app

@pytest.fixture(autouse=True)
def setup_assistant_data(client):
    client.post("/api/demo/load")

def test_assistant_why_risk(client):
    res = client.post("/api/assistant/ask", json={
        "question": "Why was case DEMO-011 classified as high risk?",
        "use_enhanced": False
    })
    assert res.status_code == 200
    data = res.json()
    assert "DEMO-011" in data["case_ids"]
    assert "HIGH" in data["answer"].upper()
    assert len(data["evidence_references"]) > 0

def test_assistant_domain_frequency(client):
    res = client.post("/api/assistant/ask", json={
        "question": "Which domain appears in multiple cases?",
        "use_enhanced": False
    })
    assert res.status_code == 200
    data = res.json()
    assert "demo-scam.test" in data["answer"]
    assert len(data["case_ids"]) > 0

def test_assistant_upi_ranking(client):
    res = client.post("/api/assistant/ask", json={
        "question": "Which UPI ID has the most reports?",
        "use_enhanced": False
    })
    assert res.status_code == 200
    data = res.json()
    assert "@" in data["answer"]
    assert len(data["case_ids"]) > 0

def test_assistant_linked_cases(client):
    res = client.post("/api/assistant/ask", json={
        "question": "Show all cases linked to demo-scam.test",
        "use_enhanced": False
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data["case_ids"]) >= 2
    assert "demo-scam.test" in data["evidence_references"]

def test_assistant_summarise_case(client):
    res = client.post("/api/assistant/ask", json={
        "question": "Summarise case DEMO-011",
        "use_enhanced": False
    })
    assert res.status_code == 200
    data = res.json()
    assert "DEMO-011" in data["case_ids"]
    assert "Summary" in data["answer"]

def test_assistant_summarise_investigation(client):
    res = client.post("/api/assistant/ask", json={
        "question": "Summarise this investigation",
        "use_enhanced": False
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data["case_ids"]) > 0
    assert "Overview" in data["answer"] or "Total" in data["answer"]

def test_assistant_website_indicators(client):
    res = client.post("/api/assistant/ask", json={
        "question": "What are the suspicious indicators in website case DEMO-041?",
        "use_enhanced": False
    })
    assert res.status_code == 200
    data = res.json()
    assert "DEMO-041" in data["case_ids"]
    assert len(data["evidence_references"]) > 0

def test_assistant_high_risk_stats(client):
    res = client.post("/api/assistant/ask", json={
        "question": "How many high risk cases?",
        "use_enhanced": False
    })
    assert res.status_code == 200
    data = res.json()
    assert "High Risk" in data["answer"]
    assert len(data["case_ids"]) > 0

def test_assistant_fallback_no_match(client):
    res = client.post("/api/assistant/ask", json={
        "question": "What is the capital of Mars?",
        "use_enhanced": False
    })
    assert res.status_code == 200
    data = res.json()
    assert data["answer"] == "No supporting records found in the database."
    assert data["case_ids"] == []

def test_assistant_enhanced_fallback(client):
    # Without API key, should gracefully serve rule-based response
    res = client.post("/api/assistant/ask", json={
        "question": "Why was case DEMO-011 classified as high risk?",
        "use_enhanced": True
    })
    assert res.status_code == 200
    data = res.json()
    assert "DEMO-011" in data["case_ids"]
    assert data["is_ai_assisted"] is False
