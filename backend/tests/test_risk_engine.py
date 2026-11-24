import json
from pathlib import Path
from app.analyzers.message import analyze_message_content
from app.analyzers.url import analyze_url_target
from app.analyzers.website import analyze_website_content
from app.config import settings

def test_risk_engine_passes_demo_dataset():
    """
    Verifies that the risk engine passes the 44-record demo set:
    - 10 genuine messages score LOW
    - 10 suspicious messages score MEDIUM or HIGH
    - 10 suspicious URLs score MEDIUM or HIGH
    - 10 website samples evaluate to expected classifications
    - 4 extra link records evaluate to expected classifications
    """
    with open(settings.DEMO_DATASET_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    results = []
    passed_count = 0
    total_evaluated = 0

    for rec in records:
        itype = rec["input_type"]
        content = rec["submitted_content"]
        expected_class = rec["expected_classification"]
        expected_risk = rec["expected_risk_level"]

        if itype == "message":
            res = analyze_message_content(content)
        elif itype == "url":
            res = analyze_url_target(content, perform_live_check=False)
        elif itype == "website":
            res = analyze_website_content(html_content=content)
        else:
            continue

        total_evaluated += 1
        predicted_risk = res["risk_level"]
        predicted_class = "genuine" if predicted_risk == "LOW" else "scam"

        # Check correctness: genuine must be LOW, scam must be MEDIUM or HIGH
        is_passed = (expected_class == predicted_class)
        if is_passed:
            passed_count += 1

        results.append({
            "case_id": rec["case_id"],
            "category": rec["category"],
            "expected_risk": expected_risk,
            "predicted_risk": predicted_risk,
            "score": res["risk_score"],
            "is_passed": is_passed
        })

    print(f"\nDemo Dataset: passes {passed_count}/{total_evaluated} records in the demo set")
    assert passed_count == total_evaluated, f"Expected all {total_evaluated} records to pass, got {passed_count}"

def test_genuine_messages_score_low():
    with open(settings.DEMO_DATASET_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    genuine_msgs = [r for r in records if r["case_id"] in [f"DEMO-{i:03d}" for i in range(1, 11)]]
    assert len(genuine_msgs) == 10

    for r in genuine_msgs:
        res = analyze_message_content(r["submitted_content"])
        assert res["risk_level"] == "LOW", f"Case {r['case_id']} scored {res['risk_level']} ({res['risk_score']} pts), expected LOW"
        assert res["risk_score"] <= 24

def test_suspicious_messages_score_medium_or_high():
    with open(settings.DEMO_DATASET_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    suspicious_msgs = [r for r in records if r["case_id"] in [f"DEMO-{i:03d}" for i in range(11, 21)]]
    assert len(suspicious_msgs) == 10

    for r in suspicious_msgs:
        res = analyze_message_content(r["submitted_content"])
        assert res["risk_level"] in ("MEDIUM", "HIGH"), f"Case {r['case_id']} scored {res['risk_level']}, expected MEDIUM/HIGH"
        assert res["risk_score"] >= 25

def test_hindi_and_hinglish_detection():
    # Hindi scam
    hi_text = "अंतिम चेतावनी: आपका बैंक खाता बंद कर दिया जाएगा। तुरंत केवाईसी अपडेट करें 90000 00004।"
    res_hi = analyze_message_content(hi_text)
    assert res_hi["risk_level"] in ("MEDIUM", "HIGH")
    assert res_hi["language"] == "hi"
    assert any("केवाईसी" in p or "चेतावनी" in p or "खाता" in p for p in res_hi["suspicious_phrases"])

    # Hinglish scam
    hinglish_text = "Aapka account block ho jayega aaj raat tak! Turant KYC update karein nahi to khata band ho jayega."
    res_hinglish = analyze_message_content(hinglish_text)
    assert res_hinglish["risk_level"] in ("MEDIUM", "HIGH")
    assert res_hinglish["language"] == "hinglish"
    assert len(res_hinglish["indicators"]) >= 2
