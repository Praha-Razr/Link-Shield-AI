import pytest
from app.linker import (
    save_case_with_relations,
    build_intelligence_graph,
    get_top_identifiers_heatlist,
    get_dashboard_statistics
)
from app.models import Case, Identifier

@pytest.fixture
def sample_linked_cases(db_session):
    # Case 1 sharing phone (+919000000001) and domain (demo-scam.test)
    case1_data = {
        "subject": "Case 1 Threat",
        "input_type": "message",
        "raw_content": "Notice 1: Call +91 90000 00001 or visit http://demo-scam.test",
        "risk_score": 75,
        "risk_level": "HIGH",
        "category": "fake_kyc",
        "language": "en",
        "indicators": [{"name": "Fake KYC", "points": 20, "explanation": "Test"}],
        "extracted_identifiers": [
            {"type": "phone", "value": "+919000000001"},
            {"type": "domain", "value": "demo-scam.test"}
        ]
    }
    save_case_with_relations(db_session, case1_data, is_demo=False, override_case_id="LS-0001")

    # Case 2 sharing the SAME phone (+919000000001) but DIFFERENT domain
    case2_data = {
        "subject": "Case 2 Loan Scam",
        "input_type": "message",
        "raw_content": "Notice 2: Loan approved! Contact +91 90000 00001 or check http://other-domain.test",
        "risk_score": 80,
        "risk_level": "HIGH",
        "category": "loan_fraud",
        "language": "en",
        "indicators": [{"name": "Loan Scam", "points": 15, "explanation": "Test"}],
        "extracted_identifiers": [
            {"type": "phone", "value": "+919000000001"},
            {"type": "domain", "value": "other-domain.test"}
        ]
    }
    save_case_with_relations(db_session, case2_data, is_demo=False, override_case_id="LS-0002")
    return db_session

def test_linker_shared_identifiers_create_graph_edges(sample_linked_cases):
    db_session = sample_linked_cases
    # Build graph
    graph = build_intelligence_graph(db_session, include_demo=False)
    nodes = graph["nodes"]
    edges = graph["edges"]

    # Verify nodes
    node_ids = [n["id"] for n in nodes]
    assert "case-LS-0001" in node_ids
    assert "case-LS-0002" in node_ids

    # Find the shared phone identifier node
    phone_id_obj = db_session.query(Identifier).filter(Identifier.value == "+919000000001").first()
    assert phone_id_obj is not None
    phone_node_id = f"ident-{phone_id_obj.id}"
    assert phone_node_id in node_ids

    # Verify that edges connect both cases to the shared phone node
    edge_sources_targets = [(e["source"], e["target"]) for e in edges]
    assert ("case-LS-0001", phone_node_id) in edge_sources_targets
    assert ("case-LS-0002", phone_node_id) in edge_sources_targets

    # other-domain.test is NOT shared by 2+ cases, so it should not appear as a bridging node
    other_domain_obj = db_session.query(Identifier).filter(Identifier.value == "other-domain.test").first()
    assert f"ident-{other_domain_obj.id}" not in node_ids

def test_heatlist_distinct_case_count(sample_linked_cases):
    db_session = sample_linked_cases
    heatlist = get_top_identifiers_heatlist(db_session, include_demo=False)
    assert len(heatlist) >= 1
    top_item = heatlist[0]
    assert top_item["value"] == "+919000000001"
    assert top_item["distinct_case_count"] == 2
    assert "fake_kyc" in top_item["categories"]
    assert "loan_fraud" in top_item["categories"]

def test_dashboard_statistics_calculation(sample_linked_cases):
    db_session = sample_linked_cases
    stats = get_dashboard_statistics(db_session)
    assert stats["total_cases"] == 2
    assert stats["high_risk_cases"] == 2
    assert stats["real_cases"] == 2
    assert stats["demo_cases"] == 0
    assert stats["cases_by_type"].get("message") == 2
    assert stats["total_shared_identifiers"] >= 1

def test_eth_address_case_insensitive_matching(db_session):
    # Case A has mixed-case checksummed ETH address
    eth_mixed = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
    case_a_data = {
        "subject": "Case A ETH",
        "input_type": "message",
        "raw_content": f"Deposit to {eth_mixed}",
        "risk_score": 50,
        "risk_level": "HIGH",
        "category": "investment_fraud",
        "language": "en",
        "indicators": [],
        "extracted_identifiers": [{"type": "crypto_wallet", "value": eth_mixed}]
    }
    case_a = save_case_with_relations(db_session, case_a_data, is_demo=False, override_case_id="LS-ETH-1")

    # Case B has lowercased version of the same ETH address
    eth_lower = eth_mixed.lower()
    case_b_data = {
        "subject": "Case B ETH",
        "input_type": "message",
        "raw_content": f"Deposit to {eth_lower}",
        "risk_score": 50,
        "risk_level": "HIGH",
        "category": "investment_fraud",
        "language": "en",
        "indicators": [],
        "extracted_identifiers": [{"type": "crypto_wallet", "value": eth_lower}]
    }
    case_b = save_case_with_relations(db_session, case_b_data, is_demo=False, override_case_id="LS-ETH-2")

    # Both cases should share the exact same Identifier row in DB!
    assert case_a.identifiers[0].id == case_b.identifiers[0].id
    # Display casing of the original record should be preserved
    assert case_a.identifiers[0].value == eth_mixed
