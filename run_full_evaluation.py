import sys
import json
from pathlib import Path

backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.analyzers.message import analyze_message_content
from app.analyzers.url import analyze_url_target
from tests.data.evaluation_samples import S_SAMPLES, G_SAMPLES, U_SAMPLES, V_SAMPLES

def evaluate_suite(name: str):
    print("=" * 80)
    print(f"EVALUATION SUITE: {name}")
    print("=" * 80)

    # 1. S1-S15
    s_passed = 0
    print("\n--- S1-S15 (Scam Messages) ---")
    for item in S_SAMPLES:
        res = analyze_message_content(item["text"])
        score = res["risk_score"]
        level = res["risk_level"]
        inds = [i["name"] for i in res["indicators"]]
        passed = (level in ("MEDIUM", "HIGH"))
        if passed:
            s_passed += 1
        st = "PASS" if passed else "FAIL (MISSED)"
        print(f"  {item['id']} [{item['name']}]: {level} ({score} pts) -> {st}")
        if not passed:
            print(f"      Text: {item['text'][:100]}...")
            print(f"      Fired: {inds}")

    # 2. G1-G10
    g_passed = 0
    print("\n--- G1-G10 (Genuine Messages) ---")
    for item in G_SAMPLES:
        res = analyze_message_content(item["text"])
        score = res["risk_score"]
        level = res["risk_level"]
        inds = [i["name"] for i in res["indicators"]]
        passed = (level == "LOW")
        if passed:
            g_passed += 1
        st = "PASS" if passed else "FAIL (FALSE POSITIVE)"
        print(f"  {item['id']} [{item['name']}]: {level} ({score} pts) -> {st}")
        if not passed:
            print(f"      Text: {item['text'][:100]}...")
            print(f"      Fired: {inds}")

    # 3. U1-U12
    u_passed = 0
    print("\n--- U1-U12 (Scam URLs) ---")
    for item in U_SAMPLES:
        res = analyze_url_target(item["url"], perform_live_check=False)
        score = res["risk_score"]
        level = res["risk_level"]
        inds = [i["name"] for i in res["indicators"]]
        passed = (level in ("MEDIUM", "HIGH"))
        if passed:
            u_passed += 1
        st = "PASS" if passed else "FAIL (MISSED)"
        print(f"  {item['id']} [{item['name']}]: {level} ({score} pts) -> {st}")
        if not passed:
            print(f"      URL: {item['url']}")
            print(f"      Fired: {inds}")

    # 4. V1-V6
    v_passed = 0
    print("\n--- V1-V6 (Genuine URLs) ---")
    for item in V_SAMPLES:
        res = analyze_url_target(item["url"], perform_live_check=False)
        score = res["risk_score"]
        level = res["risk_level"]
        inds = [i["name"] for i in res["indicators"]]
        passed = (level == "LOW")
        if passed:
            v_passed += 1
        st = "PASS" if passed else "FAIL (FALSE POSITIVE)"
        print(f"  {item['id']} [{item['name']}]: {level} ({score} pts) -> {st}")
        if not passed:
            print(f"      URL: {item['url']}")
            print(f"      Fired: {inds}")

    # 5. Held-out Set
    heldout_path = backend_dir / "tests" / "data" / "heldout_set.json"
    with open(heldout_path, "r", encoding="utf-8") as f:
        heldout_data = json.load(f)

    hs_passed = 0
    print("\n--- Held-Out Scams (HS1-HS15) ---")
    for item in heldout_data["scams"]:
        if item["type"] == "message":
            res = analyze_message_content(item["content"])
        else:
            res = analyze_url_target(item["content"], perform_live_check=False)
        score = res["risk_score"]
        level = res["risk_level"]
        inds = [i["name"] for i in res["indicators"]]
        passed = (level in ("MEDIUM", "HIGH"))
        if passed:
            hs_passed += 1
        st = "PASS" if passed else "FAIL (MISSED)"
        print(f"  {item['id']} [{item['name']}]: {level} ({score} pts) -> {st}")
        if not passed:
            print(f"      Content: {item['content'][:100]}...")
            print(f"      Fired: {inds}")

    hg_passed = 0
    print("\n--- Held-Out Genuine (HG1-HG15) ---")
    for item in heldout_data["genuine"]:
        if item["type"] == "message":
            res = analyze_message_content(item["content"])
        else:
            res = analyze_url_target(item["content"], perform_live_check=False)
        score = res["risk_score"]
        level = res["risk_level"]
        inds = [i["name"] for i in res["indicators"]]
        passed = (level == "LOW")
        if passed:
            hg_passed += 1
        st = "PASS" if passed else "FAIL (FALSE POSITIVE)"
        print(f"  {item['id']} [{item['name']}]: {level} ({score} pts) -> {st}")
        if not passed:
            print(f"      Content: {item['content'][:100]}...")
            print(f"      Fired: {inds}")

    print("\n" + "=" * 80)
    print("METRICS SUMMARY:")
    print(f"  [Set 1] Scams (S1-S15 + U1-U12) Recall: {s_passed + u_passed}/{len(S_SAMPLES) + len(U_SAMPLES)} ({(s_passed + u_passed)/(len(S_SAMPLES) + len(U_SAMPLES))*100:.1f}%)")
    print(f"  [Set 1] Genuine (G1-G10 + V1-V6) FP: {(len(G_SAMPLES) - g_passed) + (len(V_SAMPLES) - v_passed)}/{len(G_SAMPLES) + len(V_SAMPLES)} ({((len(G_SAMPLES) - g_passed) + (len(V_SAMPLES) - v_passed))/(len(G_SAMPLES) + len(V_SAMPLES))*100:.1f}%)")
    print(f"  [Set 2 - Held-out] Scams (HS1-HS15) Recall: {hs_passed}/{len(heldout_data['scams'])} ({hs_passed/len(heldout_data['scams'])*100:.1f}%)")
    print(f"  [Set 2 - Held-out] Genuine (HG1-HG15) FP: {len(heldout_data['genuine']) - hg_passed}/{len(heldout_data['genuine'])} ({(len(heldout_data['genuine']) - hg_passed)/len(heldout_data['genuine'])*100:.1f}%)")
    total_scams = len(S_SAMPLES) + len(U_SAMPLES) + len(heldout_data["scams"])
    total_scams_caught = s_passed + u_passed + hs_passed
    total_genuine = len(G_SAMPLES) + len(V_SAMPLES) + len(heldout_data["genuine"])
    total_genuine_fp = (len(G_SAMPLES) - g_passed) + (len(V_SAMPLES) - v_passed) + (len(heldout_data["genuine"]) - hg_passed)
    print(f"  OVERALL SCAM RECALL: {total_scams_caught}/{total_scams} ({total_scams_caught/total_scams*100:.1f}%)")
    print(f"  OVERALL GENUINE FP: {total_genuine_fp}/{total_genuine} ({total_genuine_fp/total_genuine*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    evaluate_suite("BASELINE (BEFORE RULE IMPROVEMENTS)")
