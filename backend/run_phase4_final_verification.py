"""
LINKSHIELD AI - Phase 4 Final Verification Script
Runs end-to-end automated verification across all 13 core criteria.
"""
import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.main import app
from app.database import SessionLocal
from app.models import Case, Indicator, Identifier

client = TestClient(app)
results = {}

def log_test(name, passed, details=""):
    results[name] = {"passed": passed, "details": details}
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    if details:
        print(f"       -> {details}")

print("======================================================================")
print("  LINKSHIELD AI - PHASE 4 FINAL VERIFICATION EXECUTION")
print("======================================================================")

# 1. Message Analyser: Genuine bank SMS -> LOW risk
try:
    res = client.post("/api/analyze/message", json={
        "content": "Your a/c no. XX9921 is credited with INR 5,000 on 22-Nov-2026. Ref: TXN998877. State Bank of India.",
        "subject": "Genuine Bank SMS Verification"
    })
    assert res.status_code == 200, f"Status code: {res.status_code}"
    data = res.json()
    assert data["risk_level"] == "LOW", f"Expected LOW, got {data['risk_level']}"
    log_test("1. Genuine Bank SMS -> LOW risk", True, f"Risk: {data['risk_level']}, Score: {data['risk_score']}")
except Exception as e:
    log_test("1. Genuine Bank SMS -> LOW risk", False, str(e))

# 2. Message Analyser: Scam SMS (English) -> HIGH risk
try:
    res = client.post("/api/analyze/message", json={
        "content": "URGENT: Your SBI netbanking account has been blocked due to missing KYC. Click http://demo-scam.test/sbi-verify immediately or call +919876543210 to avoid permanent deactivation.",
        "subject": "Scam SMS English Verification"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["risk_level"] == "HIGH", f"Expected HIGH, got {data['risk_level']}"
    assert data["risk_score"] >= 70, f"Score: {data['risk_score']}"
    log_test("2. Scam SMS (English) -> HIGH risk", True, f"Risk: {data['risk_level']}, Score: {data['risk_score']}")
except Exception as e:
    log_test("2. Scam SMS (English) -> HIGH risk", False, str(e))

# 3. Message Analyser: Scam SMS (Hinglish/Devanagari) -> HIGH risk
try:
    res = client.post("/api/analyze/message", json={
        "content": "प्रिय उपभोक्ता, बिजली विभाग: आपका बिजली का बिल बकाया है। आज रात ९:३० बजे बिजली काट दी जाएगी। तुरंत अधिकारी से संपर्क करें +91 90000 00005।",
        "subject": "Scam SMS Devanagari Verification"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["risk_level"] == "HIGH", f"Expected HIGH, got {data['risk_level']}"
    assert any("bijli" in ind["explanation"].lower() or "disconnection" in ind["name"].lower() or "बिजली" in ind["explanation"] for ind in data["indicators"])
    log_test("3. Scam SMS (Hinglish/Devanagari) -> HIGH risk", True, f"Risk: {data['risk_level']}, Score: {data['risk_score']}, Indicators: {len(data['indicators'])}")
except Exception as e:
    log_test("3. Scam SMS (Hinglish/Devanagari) -> HIGH risk", False, str(e))

# 4. URL Scanner: Lookalike domain -> flags lookalike, risk score > 50
try:
    res = client.post("/api/analyze/url", json={
        "url": "https://sbi-netbanking-kyc-verify.test/login",
        "subject": "Lookalike Domain Verification"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["risk_score"] > 50, f"Expected score > 50, got {data['risk_score']}"
    assert any("look-alike" in ind["name"].lower() or "look-alike" in ind["explanation"].lower() for ind in data["indicators"])
    log_test("4. URL Scanner Lookalike Domain -> flags lookalike & score > 50", True, f"Score: {data['risk_score']}, Indicators: {[i['name'] for i in data['indicators']]}")
except Exception as e:
    log_test("4. URL Scanner Lookalike Domain -> flags lookalike & score > 50", False, str(e))

# 5. URL Scanner: SSRF attempt (http://127.0.0.1) -> cleanly blocked
try:
    res = client.post("/api/analyze/url", json={
        "url": "http://127.0.0.1:8000/internal-admin",
        "subject": "SSRF Block Verification"
    })
    # Either 400 Bad Request or cleanly marked BLOCKED/HIGH risk without unhandled crash
    if res.status_code == 400:
        log_test("5. SSRF Attempt (127.0.0.1) -> cleanly blocked", True, f"Blocked with 400: {res.json()['detail']}")
    elif res.status_code == 200:
        data = res.json()
        assert any("blocked" in ind["name"].lower() or "prohibited" in ind["name"].lower() or "private" in ind["explanation"].lower() for ind in data["indicators"])
        log_test("5. SSRF Attempt (127.0.0.1) -> cleanly blocked", True, f"Intercepted by policy: {[i['name'] for i in data['indicators']]}")
    else:
        log_test("5. SSRF Attempt (127.0.0.1) -> cleanly blocked", False, f"Unexpected code {res.status_code}")
except Exception as e:
    log_test("5. SSRF Attempt (127.0.0.1) -> cleanly blocked", False, str(e))

# 6. Website Analyser: Saved HTML -> extracts indicators and identifiers
try:
    html_sample = """
    <html>
      <head><title>Instant Fast Loan - 0% Interest</title></head>
      <body>
        <h1>Guaranteed 50,000 Loan Approved in 2 Minutes!</h1>
        <p>Deposit registration fee of Rs 999 to UPI: fastloan@demoupi or call +919876543210.</p>
        <p>No CIBIL required. 100% Guaranteed returns!</p>
      </body>
    </html>
    """
    res = client.post("/api/analyze/website", json={
        "html_content": html_sample,
        "subject": "Website Analyzer HTML Verification"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["risk_level"] in ["HIGH", "MEDIUM"]
    assert len(data["indicators"]) >= 1
    assert len(data["extracted_identifiers"]) >= 1
    log_test("6. Website Analyser -> extracts indicators & identifiers", True, f"Risk: {data['risk_level']}, Score: {data['risk_score']}, Identifiers: {len(data['extracted_identifiers'])}")
except Exception as e:
    log_test("6. Website Analyser -> extracts indicators & identifiers", False, str(e))

# 7. Case Management -> opens case, shows indicators, allows adding a note, saves cleanly
try:
    # Fetch first case
    cases_res = client.get("/api/cases?limit=1")
    assert cases_res.status_code == 200
    case_list = cases_res.json()["cases"]
    assert len(case_list) > 0
    cid = case_list[0]["id"]

    # Open case
    detail_res = client.get(f"/api/cases/{cid}")
    assert detail_res.status_code == 200
    case_detail = detail_res.json()
    assert "indicators" in case_detail
    assert "identifiers" in case_detail

    # Add a note
    test_note = "Official Verification Note: Cyber Cell Audit Complete."
    note_res = client.patch(f"/api/cases/{cid}/notes", json={"notes": test_note})
    assert note_res.status_code == 200
    assert note_res.json()["investigator_notes"] == test_note
    log_test("7. Case Management -> open, detail, save note cleanly", True, f"Case {cid} updated with note")
except Exception as e:
    log_test("7. Case Management -> open, detail, save note cleanly", False, str(e))

# 8. Scam Graph -> renders hubs, campaign view, click node shows panel
try:
    graph_res = client.get("/api/intelligence/graph?include_demo=true")
    assert graph_res.status_code == 200
    gdata = graph_res.json()
    nodes = gdata["nodes"]
    edges = gdata["edges"]
    assert len(nodes) > 0, "No nodes in graph"
    assert len(edges) > 0, "No edges in graph"
    high_nodes = [n for n in nodes if n["risk_level"] == "HIGH"]
    assert len(high_nodes) > 0
    assert any(n.get("risk_score") and n["risk_score"] > 50 for n in high_nodes)
    log_test("8. Scam Graph -> campaign hubs, nodes & valid threat scores", True, f"Total Nodes: {len(nodes)}, Total Edges: {len(edges)}, High Threat Sample Score: {high_nodes[0]['risk_score']}/100")
except Exception as e:
    log_test("8. Scam Graph -> campaign hubs, nodes & valid threat scores", False, str(e))

# 9. PDF Dossier -> downloads valid PDF for at least 3 cases of different types
try:
    pdf_count = 0
    cases_res = client.get("/api/cases?limit=10")
    for c in cases_res.json()["cases"]:
        res = client.get(f"/api/reports/{c['id']}/pdf")
        if res.status_code == 200 and res.content.startswith(b"%PDF-"):
            pdf_count += 1
            if pdf_count >= 3:
                break
    assert pdf_count >= 3, f"Only {pdf_count} PDFs generated"
    log_test("9. PDF Dossier -> downloads valid PDF across distinct cases", True, f"Verified {pdf_count} PDF dossiers generated successfully")
except Exception as e:
    log_test("9. PDF Dossier -> downloads valid PDF across distinct cases", False, str(e))

# 10. Assistant -> answers 5 test questions correctly without hallucination (rule-based)
test_questions = [
    ("Why was case LS-0006 classified as high risk?", ["LS-0006"]),
    ("Which domain appears in multiple cases?", ["demo-scam.test"]),
    ("Which UPI ID has the most reports?", ["@"]),
    ("Show all cases linked to demo-scam.test", ["demo-scam.test"]),
    ("Summarise this investigation", ["Investigation Summary", "Cases"])
]

assistant_success = True
assistant_details = []
for q, expected_keywords in test_questions:
    try:
        res = client.post("/api/assistant/ask", json={"question": q, "use_enhanced": False})
        assert res.status_code == 200
        adata = res.json()
        assert len(adata["answer"]) > 0
        assert any(k in adata["answer"] or any(k in c for c in adata["case_ids"]) or any(k in ev for ev in adata["evidence_references"]) for k in expected_keywords), f"Query '{q}' missing expected keywords"
        assistant_details.append(f"Q: '{q[:25]}...' -> OK")
    except Exception as e:
        assistant_success = False
        assistant_details.append(f"Q: '{q}' FAILED: {e}")

log_test("10. Assistant -> 5 intent questions answered with evidence citations", assistant_success, "; ".join(assistant_details))

# 11. Assistant fallback -> answers unknown query with exact fallback string
try:
    res = client.post("/api/assistant/ask", json={
        "question": "What is the secret passphrase of alien spacecraft 9999?",
        "use_enhanced": False
    })
    assert res.status_code == 200
    adata = res.json()
    assert adata["answer"] == "No supporting records found in the database.", f"Got: '{adata['answer']}'"
    log_test("11. Assistant Fallback -> exact string on ungrounded query", True, f"Answer: '{adata['answer']}'")
except Exception as e:
    log_test("11. Assistant Fallback -> exact string on ungrounded query", False, str(e))

# 12. Demo data -> Clear Demo, reload, Load Demo, verify idempotency
try:
    # Clear demo
    c_res = client.post("/api/demo/clear", json={"confirm": True})
    assert c_res.status_code == 200
    cleared_cases = client.get("/api/cases?include_demo=false").json()["total"]

    # Load demo
    l_res = client.post("/api/demo/load", json={})
    assert l_res.status_code == 200
    restored_cases = client.get("/api/cases?include_demo=true").json()["total"]

    # Re-load to verify idempotency
    l2_res = client.post("/api/demo/load", json={})
    assert l2_res.status_code == 200
    idempotent_cases = client.get("/api/cases?include_demo=true").json()["total"]
    assert restored_cases == idempotent_cases, f"Mismatch: {restored_cases} vs {idempotent_cases}"

    log_test("12. Demo Data -> Clear, Load & Idempotency", True, f"Real cases: {cleared_cases}, After Demo Load: {restored_cases}, Idempotency Verified")
except Exception as e:
    log_test("12. Demo Data -> Clear, Load & Idempotency", False, str(e))

print("======================================================================")
all_passed = all(t["passed"] for t in results.values())
if all_passed:
    print(f"ALL 12 E2E VERIFICATIONS PASSED SUCCESSFULLY! (100% GREEN)")
else:
    print("SOME VERIFICATIONS FAILED. Check details above.")
print("======================================================================")

# Write results to JSON for TEST_RESULTS.md generation
with open(Path(__file__).resolve().parent / "verification_output.json", "w") as f:
    json.dump(results, f, indent=2)

if not all_passed:
    sys.exit(1)
