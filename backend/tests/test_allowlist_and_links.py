import pytest
from app.allowlist import is_ifsc_code, is_legitimate_identifier, is_linkable_identifier

def test_ifsc_detection():
    assert is_ifsc_code("bank_account", "IFSC:SBIN0001234") is True
    assert is_ifsc_code("ifsc", "SBIN0001234") is True
    assert is_ifsc_code("bank_account", "HDFC0000240") is True
    assert is_ifsc_code("bank_account", "ICIC0000001") is True
    assert is_ifsc_code("bank_account", "123456789012") is False
    assert is_ifsc_code("phone", "+919876543210") is False

def test_legitimate_identifiers_classification():
    # Domains
    assert is_legitimate_identifier("domain", "sbi.co.in") is True
    assert is_legitimate_identifier("domain", "onlinesbi.sbi") is True
    assert is_legitimate_identifier("domain", "hdfcbank.com") is True
    assert is_legitimate_identifier("domain", "corp.sbi.co.in") is True  # subdomain
    assert is_legitimate_identifier("domain", "cybercrime.gov.in") is True
    assert is_legitimate_identifier("domain", "demo-scam.test") is False
    assert is_legitimate_identifier("domain", "fake-sbi-portal.xyz") is False

    # Emails
    assert is_legitimate_identifier("email", "contactus@sbi.co.in") is True
    assert is_legitimate_identifier("email", "support@hdfcbank.com") is True
    assert is_legitimate_identifier("email", "alert@cybercrime.gov.in") is True
    assert is_legitimate_identifier("email", "scammer@protonmail.com") is False

    # Phones
    assert is_legitimate_identifier("phone", "1930") is True
    assert is_legitimate_identifier("phone", "18001234") is True
    assert is_legitimate_identifier("phone", "+919000000001") is False

def test_linkable_identifiers_logic():
    # Unlinkable
    assert is_linkable_identifier("bank_account", "IFSC:SBIN0001234") is False
    assert is_linkable_identifier("domain", "sbi.co.in") is False
    assert is_linkable_identifier("email", "contactus@sbi.co.in") is False
    assert is_linkable_identifier("phone", "1930") is False

    # Linkable scam indicators
    assert is_linkable_identifier("domain", "demo-scam.test") is True
    assert is_linkable_identifier("phone", "+919000000001") is True
    assert is_linkable_identifier("upi", "demo.pay@demoupi") is True
    assert is_linkable_identifier("bank_account", "987654321098") is True
    assert is_linkable_identifier("crypto_wallet", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa") is True

def test_demo_graph_and_heatlist_filtering(client):
    # Load demo dataset into fresh test db
    load_res = client.post("/api/demo/load")
    assert load_res.status_code == 200

    # 1. Check graph
    graph_res = client.get("/api/intelligence/graph?min_cases=2")
    assert graph_res.status_code == 200
    graph_data = graph_res.json()

    graph_labels = [n.get("label", "").lower() for n in graph_data["nodes"]]
    graph_values = [n.get("value", "").lower() for n in graph_data["nodes"]]

    # Legitimate entities and IFSC must NOT be in the graph
    for val in graph_values:
        assert "sbi.co.in" not in val, f"Found legitimate domain in graph: {val}"
        assert "contactus@sbi.co.in" not in val, f"Found legitimate email in graph: {val}"
        assert "ifsc" not in val, f"Found IFSC code in graph: {val}"

    # Scam entities MUST be present in the graph
    assert any("demo-scam.test" in v for v in graph_values), "Expected demo-scam.test in graph nodes"
    assert any("+919000000001" in v for v in graph_values), "Expected +919000000001 in graph nodes"
    assert any("demo.pay@demoupi" in v for v in graph_values), "Expected demo.pay@demoupi in graph nodes"

    # 2. Check threat heatlist
    heat_res = client.get("/api/intelligence/heatlist")
    assert heat_res.status_code == 200
    heat_json = heat_res.json()
    heat_items = heat_json.get("items", [])

    for item in heat_items:
        val = item["value"].lower()
        assert val != "sbi.co.in", "sbi.co.in should not appear in threat heatlist"
        assert val != "contactus@sbi.co.in", "contactus@sbi.co.in should not appear in threat heatlist"
        assert not val.startswith("ifsc"), "IFSC should not appear in threat heatlist"

    # Top scam items must be ranked
    heat_values = [item["value"].lower() for item in heat_items]
    assert "demo-scam.test" in heat_values
    assert "+919000000001" in heat_values
    assert "demo.pay@demoupi" in heat_values

    # 3. Check that genuine cases do NOT link to scam cases
    # Search for genuine cases (DEMO-001 through DEMO-020 are genuine)
    for c_id in ["DEMO-001", "DEMO-002", "DEMO-003", "DEMO-004"]:
        detail_res = client.get(f"/api/cases/{c_id}")
        if detail_res.status_code == 200:
            case_info = detail_res.json()
            assert case_info["risk_level"] == "LOW"
            for rel in case_info.get("related_cases", []):
                assert rel.get("risk_level") == "LOW", f"Genuine case {c_id} linked to non-LOW case: {rel}"
