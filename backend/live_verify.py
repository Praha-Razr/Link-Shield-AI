import json
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Case

client = TestClient(app)

def run_live_verification():
    print("=== LinkShield AI Backend Live Verification ===")

    # 1. Health check
    res_health = client.get("/api/health")
    print(f"\n1. GET /api/health -> {res_health.status_code}")
    print(json.dumps(res_health.json(), indent=2))
    assert res_health.status_code == 200

    # 2. Load Demo Data
    res_load = client.post("/api/demo/load")
    print(f"\n2. POST /api/demo/load -> {res_load.status_code}")
    print(json.dumps(res_load.json(), indent=2))
    assert res_load.status_code == 200

    # 3. Check Dashboard Stats (real database numbers)
    res_stats = client.get("/api/dashboard/stats")
    print(f"\n3. GET /api/dashboard/stats -> {res_stats.status_code}")
    stats_data = res_stats.json()
    print(json.dumps(stats_data, indent=2))
    assert res_stats.status_code == 200
    assert stats_data["total_cases"] >= 44
    assert stats_data["total_shared_identifiers"] >= 1

    # 4. Analyze New Message (Real case)
    sample_msg = {
        "content": "ALERT: Your HDFC bank account will be blocked today due to pending KYC! Transfer processing fee to UPI officer.verify@demoupi or contact +91 90000 00001 immediately.",
        "subject": "Urgent HDFC Block Warning"
    }
    res_msg = client.post("/api/analyze/message", json=sample_msg)
    print(f"\n4. POST /api/analyze/message -> {res_msg.status_code}")
    msg_data = res_msg.json()
    print(json.dumps({
        "case_id": msg_data["case_id"],
        "subject": msg_data["subject"],
        "risk_score": msg_data["risk_score"],
        "risk_level": msg_data["risk_level"],
        "category": msg_data["category"],
        "indicators": [f"{i['name']} (+{i['points']} pts)" for i in msg_data["indicators"]],
        "extracted_identifiers": [f"{i['type']}: {i['value']}" for i in msg_data["extracted_identifiers"]],
        "similarity_matches": msg_data["similarity_matches"],
        "recommendations": msg_data["safety_recommendations"]
    }, indent=2))
    assert res_msg.status_code == 200
    assert msg_data["risk_level"] == "HIGH"

    # 5. Analyze URL
    sample_url = {
        "url": "http://sbi-netbanking-kyc-verify.test/login",
        "perform_live_check": False
    }
    res_url = client.post("/api/analyze/url", json=sample_url)
    print(f"\n5. POST /api/analyze/url -> {res_url.status_code}")
    url_data = res_url.json()
    print(json.dumps({
        "case_id": url_data["case_id"],
        "subject": url_data["subject"],
        "risk_score": url_data["risk_score"],
        "risk_level": url_data["risk_level"],
        "indicators": [f"{i['name']} (+{i['points']} pts)" for i in url_data["indicators"]]
    }, indent=2))
    assert res_url.status_code == 200

    # 6. Intelligence Graph
    res_graph = client.get("/api/intelligence/graph?include_demo=true")
    print(f"\n6. GET /api/intelligence/graph -> {res_graph.status_code}")
    graph_data = res_graph.json()
    print(f"Graph Nodes Count: {len(graph_data['nodes'])}, Edges Count: {len(graph_data['edges'])}")
    assert len(graph_data["nodes"]) >= 3
    assert len(graph_data["edges"]) >= 3

    # 7. Intelligence Heatlist (Frequently reported identifiers)
    res_heat = client.get("/api/intelligence/heatlist?include_demo=true&limit=5")
    print(f"\n7. GET /api/intelligence/heatlist -> {res_heat.status_code}")
    heat_data = res_heat.json()
    for item in heat_data["items"][:3]:
        print(f"  Identifier: {item['type']}='{item['value']}', Distinct Case Count: {item['distinct_case_count']}, Categories: {item['categories']}")
    assert heat_data["total"] >= 1

    # 8. Query Case Detail
    res_case = client.get(f"/api/cases/{msg_data['case_id']}")
    print(f"\n8. GET /api/cases/{msg_data['case_id']} -> {res_case.status_code}")
    assert res_case.status_code == 200

    # 9. Patch Investigator Notes
    res_patch = client.patch(f"/api/cases/{msg_data['case_id']}/notes", json={
        "notes": "Verified by Investigator Sharma. Cross-referenced with cyber cell incident FIR-2026/88."
    })
    print(f"\n9. PATCH /api/cases/{msg_data['case_id']}/notes -> {res_patch.status_code}")
    assert res_patch.status_code == 200

    # 10. PDF Report Stub
    res_pdf = client.get(f"/api/reports/{msg_data['case_id']}/pdf")
    print(f"\n10. GET /api/reports/.../pdf -> {res_pdf.status_code} (Phase 3 Stub)")
    assert res_pdf.status_code == 501

    print("\n✅ ALL LIVE VERIFICATION CHECKS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_live_verification()
