import json
import io

def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["app"] == "LinkShield AI"

def test_api_analyze_message(client):
    payload = {
        "content": "URGENT: SBI account blocked today! Update KYC at http://demo-scam.test/kyc or call +91 90000 00001",
        "subject": "Test Urgent Scam"
    }
    res = client.post("/api/analyze/message", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["risk_level"] == "HIGH"
    assert data["risk_score"] >= 50
    assert len(data["indicators"]) >= 2
    assert any(ind["points"] > 0 for ind in data["indicators"])
    assert data["evidence"]["content_sha256"] is not None

def test_api_analyze_url(client):
    payload = {
        "url": "http://sbi-fake-login.test/verify",
        "perform_live_check": False
    }
    res = client.post("/api/analyze/url", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["risk_level"] in ("MEDIUM", "HIGH")
    assert len(data["indicators"]) >= 1

def test_api_analyze_website_html_content(client):
    html = "<html><body><h1>Guaranteed Return Investment</h1><p>Send 1000 get 10000 back! Pay to UPI demo.pay@demoupi</p></body></html>"
    res = client.post("/api/analyze/website", json={"html_content": html, "subject": "Test Site"})
    assert res.status_code == 200
    data = res.json()
    assert data["risk_level"] in ("MEDIUM", "HIGH")
    assert any(item["value"] == "demo.pay@demoupi" for item in data["extracted_identifiers"])

def test_api_cases_list_and_detail(client):
    # Insert a case
    msg_res = client.post("/api/analyze/message", json={"content": "Notice 100: Call 9000000021"})
    case_id = msg_res.json()["case_id"]

    # List cases
    list_res = client.get("/api/cases?page=1&page_size=10")
    assert list_res.status_code == 200
    cases_data = list_res.json()
    assert cases_data["total"] >= 1
    assert any(c["id"] == case_id for c in cases_data["cases"])

    # Detail
    detail_res = client.get(f"/api/cases/{case_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == case_id

def test_api_patch_notes(client):
    msg_res = client.post("/api/analyze/message", json={"content": "Notice 101: Call 9000000022"})
    case_id = msg_res.json()["case_id"]

    patch_res = client.patch(f"/api/cases/{case_id}/notes", json={"notes": "Investigated by Officer Sharma on 22-Nov."})
    assert patch_res.status_code == 200
    assert patch_res.json()["investigator_notes"] == "Investigated by Officer Sharma on 22-Nov."

    detail_res = client.get(f"/api/cases/{case_id}")
    assert detail_res.json()["investigator_notes"] == "Investigated by Officer Sharma on 22-Nov."

def test_api_pdf_report_real(client):
    # First ensure a case exists
    res_msg = client.post("/api/analyze/message", json={
        "content": "Emergency Scam: Call +919876543210 to prevent account block. Pay UPI to demo.scam@demoupi",
        "subject": "PDF Test Case"
    })
    assert res_msg.status_code == 200
    case_id = res_msg.json()["case_id"]

    res_pdf = client.get(f"/api/reports/{case_id}/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert res_pdf.content.startswith(b"%PDF")
    assert len(res_pdf.content) > 1000

def test_api_import_json(client):
    external_data = [
        {
            "content": "Emergency: Electricity connection disconnected tonight! Pay bill to upi elect.bill@demoupi",
            "input_type": "message",
            "subject": "External Complaint #991"
        }
    ]
    file_bytes = json.dumps(external_data).encode("utf-8")
    files = {"file": ("external.json", io.BytesIO(file_bytes), "application/json")}
    res = client.post("/api/import", files=files)
    assert res.status_code == 200
    assert res.json()["imported_count"] == 1

def test_api_case_detail_related_cases(client):
    # Case 1 with shared phone +91 91111 22222
    res1 = client.post("/api/analyze/message", json={
        "content": "Notice A: Contact officer at 9111122222 immediately.",
        "subject": "Case Alpha"
    })
    case1_id = res1.json()["case_id"]

    # Case 2 sharing the same phone
    res2 = client.post("/api/analyze/message", json={
        "content": "Notice B: Urgent loan enquiry call 9111122222.",
        "subject": "Case Beta"
    })
    case2_id = res2.json()["case_id"]

    # Inspect Case 1
    detail1 = client.get(f"/api/cases/{case1_id}").json()
    assert any(rel["case_id"] == case2_id for rel in detail1["related_cases"])
    partner_rel = next(r for r in detail1["related_cases"] if r["case_id"] == case2_id)
    assert any("+919111122222" in s for s in partner_rel["shared_identifiers"])

def test_case_search_id_normalization_and_identifiers(client, db_session):
    from datetime import datetime, timezone
    from app.models import Case

    # Ensure LS-0032 exists in database
    existing_case = db_session.query(Case).filter(Case.id == "LS-0032").first()
    if not existing_case:
        c32 = Case(
            id="LS-0032",
            subject="Doctor Appointment Reminder",
            input_type="message",
            raw_content="Doctor appointment reminder: confirm your slot at http://clinic-fake.test or call +919876500032",
            content_sha256="fakehash32",
            created_at=datetime.now(timezone.utc),
            risk_score=75,
            risk_level="HIGH",
            category="phishing_link",
            status="NEW",
            is_demo=False,
            language="en"
        )
        db_session.add(c32)
        db_session.commit()

    # Ensure demo data is loaded for DEMO-001
    client.post("/api/demo/load")

    # 1. Test LS0032 variations (must all find LS-0032)
    for variant in ["LS0032", "ls-0032", "LS 0032", "ls0032"]:
        res = client.get(f"/api/cases?q={variant}")
        assert res.status_code == 200
        data = res.json()
        assert any(c["id"] == "LS-0032" for c in data["cases"]), f"Failed to find LS-0032 with query '{variant}'"

    # 2. Test DEMO0001 variations (must all find DEMO-001)
    for variant in ["DEMO0001", "demo-001", "DEMO 001", "demo001"]:
        res = client.get(f"/api/cases?q={variant}")
        assert res.status_code == 200
        data = res.json()
        assert any(c["id"] == "DEMO-001" for c in data["cases"]), f"Failed to find DEMO-001 with query '{variant}'"

    # 3. Test identifier search
    res_ident = client.get("/api/cases?q=demo-scam.test")
    assert res_ident.status_code == 200
    assert res_ident.json()["total"] >= 1


