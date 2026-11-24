import json
from pathlib import Path
from app.analyzers.message import analyze_message_content
from app.analyzers.url import analyze_url_target
from tests.data.evaluation_samples import S_SAMPLES, G_SAMPLES, U_SAMPLES, V_SAMPLES

HELDOUT_PATH = Path(__file__).resolve().parent / "data" / "heldout_set.json"

def test_heldout_scams_recall():
    """Verifies that all 15 held-out scam cases are correctly detected as MEDIUM or HIGH."""
    with open(HELDOUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    scams = data.get("scams", [])
    assert len(scams) >= 15, "Expected at least 15 held-out scam cases"

    for sample in scams:
        if sample["type"] == "message":
            res = analyze_message_content(sample["content"])
        else:
            res = analyze_url_target(sample["content"], perform_live_check=False)

        risk = res["risk_level"]
        score = res["risk_score"]
        assert risk in ("MEDIUM", "HIGH"), f"Held-out scam {sample['id']} [{sample['name']}] scored {risk} ({score} pts), expected MEDIUM or HIGH"

def test_heldout_genuine_specificity():
    """Verifies that all 15 held-out genuine cases stay safely classified as LOW."""
    with open(HELDOUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    genuine = data.get("genuine", [])
    assert len(genuine) >= 15, "Expected at least 15 held-out genuine cases"

    for sample in genuine:
        if sample["type"] == "message":
            res = analyze_message_content(sample["content"])
        else:
            res = analyze_url_target(sample["content"], perform_live_check=False)

        risk = res["risk_level"]
        score = res["risk_score"]
        assert risk == "LOW", f"Held-out genuine {sample['id']} [{sample['name']}] false positive! Scored {risk} ({score} pts), expected LOW. Fired: {[i['name'] for i in res.get('indicators', [])]}"

def test_sg_uv_evaluation_set():
    """Verifies that the entire S1-S15, G1-G10, U1-U12, V1-V6 suite meets recall and specificity targets."""
    # S1-S15
    for s in S_SAMPLES:
        res = analyze_message_content(s["text"])
        assert res["risk_level"] in ("MEDIUM", "HIGH"), f"{s['id']} scored {res['risk_level']}, expected MEDIUM/HIGH"

    # G1-G10
    for g in G_SAMPLES:
        res = analyze_message_content(g["text"])
        assert res["risk_level"] == "LOW", f"{g['id']} scored {res['risk_level']}, expected LOW"

    # U1-U12
    for u in U_SAMPLES:
        res = analyze_url_target(u["url"], perform_live_check=False)
        assert res["risk_level"] in ("MEDIUM", "HIGH"), f"{u['id']} scored {res['risk_level']}, expected MEDIUM/HIGH"

    # V1-V6
    for v in V_SAMPLES:
        res = analyze_url_target(v["url"], perform_live_check=False)
        assert res["risk_level"] == "LOW", f"{v['id']} scored {res['risk_level']}, expected LOW"
