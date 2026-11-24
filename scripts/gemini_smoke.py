"""
LinkShield AI - Live Gemini Verification & Smoke Test Script
Executes end-to-end smoke tests against live Gemini API using settings from backend/.env.
"""
import sys
import os
from pathlib import Path

# Set up paths
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.database import SessionLocal
from app.assistant import ask_assistant, get_assistant_status
from app.analyzers.message import analyze_message_content
from app.analyzers.ai_opinion import evaluate_ai_second_opinion

def print_separator(title=""):
    print("\n" + "=" * 65)
    if title:
        print(f"  {title}")
        print("=" * 65)

def run_smoke():
    print_separator("LINKSHIELD AI - GEMINI SMOKE TEST SUITE")
    print(f"Configured Model : {settings.GEMINI_MODEL}")
    print(f"API Key Present  : {bool(settings.GEMINI_API_KEY)}")
    print(f"Analysis Enabled : {settings.AI_ASSIST_ANALYSIS}")
    print(f"Real Cases AI    : {settings.ALLOW_EXTERNAL_AI_FOR_REAL_CASES}")

    if not settings.GEMINI_API_KEY:
        print("\n[!] WARNING: GEMINI_API_KEY is not configured in backend/.env.")
        print("Tests will demonstrate verified offline fallback behavior.")

    db = SessionLocal()
    try:
        # Step 0: Status Check
        print_separator("PART 0: LIVE STATUS CHECK (/api/assistant/status)")
        status = get_assistant_status(db)
        print(f"Status Result: {status}")
        if status.get("status") == "ok":
            print("[+] Gemini API is connected and responding normally.")
        else:
            print(f"[-] Gemini status: {status.get('status')} - {status.get('error')}")

        # Test 1: Friendly Greeting
        print_separator("TEST 1: CONVERSATIONAL GREETING ('hi')")
        res1 = ask_assistant(db, "hi", use_enhanced=True)
        print(f"Mode         : {res1.mode}")
        print(f"AI-Assisted  : {res1.is_ai_assisted}")
        print(f"Response     : {res1.answer}")

        # Test 2: Shared Domains Query
        print_separator("TEST 2: SHARED DOMAINS ('Which domain appears in multiple cases?')")
        res2 = ask_assistant(db, "Which domain appears in multiple cases?", use_enhanced=True)
        print(f"Mode         : {res2.mode}")
        print(f"AI-Assisted  : {res2.is_ai_assisted}")
        print(f"Cited Cases  : {res2.case_ids}")
        print(f"Response     : {res2.answer}")

        # Test 3: Specific Case Forensic Reasoning
        print_separator("TEST 3: CASE FORENSIC REASONING ('Why was DEMO-011 high risk?')")
        res3 = ask_assistant(db, "Why was DEMO-011 high risk?", use_enhanced=True)
        print(f"Mode         : {res3.mode}")
        print(f"AI-Assisted  : {res3.is_ai_assisted}")
        print(f"Cited Cases  : {res3.case_ids}")
        print(f"Response     : {res3.answer}")

        # Test 4: Made-up Case Citation Rejection Guard
        print_separator("TEST 4: HALLUCINATION GUARD ('LS-9999' - must say not found)")
        res4 = ask_assistant(db, "Tell me about case LS-9999", use_enhanced=True)
        print(f"Mode         : {res4.mode}")
        print(f"AI-Assisted  : {res4.is_ai_assisted}")
        print(f"Cited Cases  : {res4.case_ids}")
        print(f"Fallback Msg : {res4.fallback_reason}")
        print(f"Response     : {res4.answer}")
        assert "LS-9999" not in res4.case_ids, "Hallucinated ID should never be cited!"

        # Test 5: Real Message Analysis with AI Second Opinion
        print_separator("TEST 5: REAL MESSAGE ANALYSIS + AI SECOND OPINION")
        sample_msg = "Mom this is my new number, old one is not working. Need Rs 8,000 right now for a hospital bill, send to this account and I will call you tonight."
        print(f"Input Message:\n\"{sample_msg}\"")

        # 5a. Base rule-based analysis
        analysis_data = analyze_message_content(sample_msg)
        print(f"\nRule Engine Initial Assessment:")
        print(f"  Score: {analysis_data['risk_score']} / 100")
        print(f"  Level: {analysis_data['risk_level']}")
        print(f"  Indicators: {[i['name'] for i in analysis_data['indicators']]}")

        # 5b. AI Second Opinion
        opinion, escalated_data = evaluate_ai_second_opinion(sample_msg, "message", analysis_data)
        print(f"\nAI Second Opinion Result:")
        print(f"  Status          : {opinion.get('status')}")
        print(f"  Scam Likelihood : {opinion.get('scam_likelihood')}")
        print(f"  Category        : {opinion.get('category')}")
        print(f"  Confidence      : {opinion.get('confidence')}")
        print(f"  Reasons         : {opinion.get('reasons')}")
        print(f"  Disclaimer      : {opinion.get('disclaimer')}")

        print(f"\nFinal Post-AI Threat Level:")
        print(f"  Final Score     : {escalated_data['risk_score']} / 100")
        print(f"  Final Level     : {escalated_data['risk_level']}")
        print(f"  Final Indicators: {[i['name'] for i in escalated_data['indicators']]}")
        print(f"  Recommendations : {escalated_data['safety_recommendations']}")

        print_separator("ALL SMOKE TESTS EXECUTED SUCCESSFULLY")

    finally:
        db.close()

if __name__ == "__main__":
    run_smoke()
