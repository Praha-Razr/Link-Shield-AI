import pytest
from app.risk.engine import (
    get_verified_official_info,
    get_safety_recommendations,
    get_registered_domain,
    is_official_domain
)
from app.analyzers.url import analyze_url_target
from app.analyzers.message import analyze_message_content
from app.reports.pdf import generate_case_pdf_report

def test_registered_domain_extraction():
    assert get_registered_domain("www.sbi.co.in") == "sbi.co.in"
    assert get_registered_domain("sbi.co.in") == "sbi.co.in"
    assert get_registered_domain("irctc.co.in") == "irctc.co.in"
    assert get_registered_domain("cybercrime.gov.in") == "cybercrime.gov.in"
    assert get_registered_domain("amazon.in") == "amazon.in"
    assert get_registered_domain("sbi-bank.com.fake-domain.top") == "fake-domain.top"
    assert get_registered_domain("www.hdfcbank.com.secure-login.cfd") == "secure-login.cfd"

def test_verified_official_domains():
    # Exact genuine official domains with HTTPS and 0 risk
    sbi_info = get_verified_official_info("https://www.sbi.co.in", scheme="https", risk_score=0, indicators=[])
    assert sbi_info is not None
    assert sbi_info["is_verified"] is True
    assert "SBI" in sbi_info["brand_name"]
    assert "official website" in sbi_info["badge_title"]

    irctc_info = get_verified_official_info("https://www.irctc.co.in", scheme="https", risk_score=0, indicators=[])
    assert irctc_info is not None
    assert irctc_info["is_verified"] is True
    assert "IRCTC" in irctc_info["brand_name"]

    cybercrime_info = get_verified_official_info("https://cybercrime.gov.in", scheme="https", risk_score=0, indicators=[])
    assert cybercrime_info is not None
    assert cybercrime_info["is_verified"] is True

    amazon_info = get_verified_official_info("https://www.amazon.in/your-orders", scheme="https", risk_score=0, indicators=[])
    assert amazon_info is not None
    assert amazon_info["is_verified"] is True
    assert "Amazon" in amazon_info["brand_name"]

def test_unverified_lookalikes_and_insecure():
    # Substring / look-alike domains MUST NOT match
    fake_sbi = get_verified_official_info("https://sbi-bank.com.fake-domain.top", scheme="https", risk_score=0, indicators=[])
    assert fake_sbi is None

    fake_hdfc = get_verified_official_info("https://www.hdfcbank.com.secure-login.cfd", scheme="https", risk_score=0, indicators=[])
    assert fake_hdfc is None

    # HTTP scheme (unencrypted) MUST NOT get verified badge
    http_sbi = get_verified_official_info("http://www.sbi.co.in", scheme="http", risk_score=0, indicators=[])
    assert http_sbi is None

    # If indicators fired or score > 0, MUST NOT get badge
    flagged = get_verified_official_info("https://www.sbi.co.in", scheme="https", risk_score=20, indicators=[{"name": "test"}])
    assert flagged is None

def test_safety_recommendations_by_level():
    high_recs = get_safety_recommendations("HIGH")
    assert any("Do not click links" in r for r in high_recs)
    assert any("1930" in r or "cybercrime.gov.in" in r for r in high_recs)

    med_recs = get_safety_recommendations("MEDIUM")
    assert any("Suspicious: be careful" in r for r in med_recs)
    assert any("official app/website" in r for r in med_recs)

    low_recs = get_safety_recommendations("LOW")
    # Must NOT have alarming warnings for LOW
    assert not any("Do not click" in r for r in low_recs)
    assert not any("Do not pay" in r for r in low_recs)
    assert not any("1930" in r for r in low_recs)
    # Must have calm precautionary advice
    assert any("open links through the official app or website" in r for r in low_recs)
    assert any("Low risk does not guarantee safety" in r for r in low_recs)

def test_analyzers_integration():
    # URL Analyzer with verified domain
    url_res = analyze_url_target("https://www.sbi.co.in")
    assert url_res["risk_level"] == "LOW"
    assert url_res["risk_score"] == 0
    assert url_res["verified_official"] is not None
    assert url_res["verified_official"]["is_verified"] is True
    assert not any("Do not click" in r for r in url_res["safety_recommendations"])

    # High-risk phishing URL
    scam_res = analyze_url_target("http://sbi-kyc-update.xyz/login")
    assert scam_res["risk_level"] == "HIGH"
    assert scam_res["verified_official"] is None
    assert any("Do not click" in r for r in scam_res["safety_recommendations"])

    # Message Analyzer with link to amazon.in
    msg_res = analyze_message_content("Track your order at https://www.amazon.in/your-orders")
    assert msg_res["risk_level"] == "LOW"
    assert any(link.get("is_official") for link in msg_res.get("verified_links", []))
    assert not any("Do not click" in r for r in msg_res["safety_recommendations"])

    # Genuine bank transaction message
    genuine_msg = analyze_message_content("Dear Customer, Rs 15,000 credited to your account. Avail balance: Rs 45,200. - SBI")
    assert genuine_msg["risk_level"] == "LOW"
    assert not any("Do not click" in r for r in genuine_msg["safety_recommendations"])

def test_pdf_dossier_generation_both_levels():
    low_case = {
        "case_id": "CASE-TEST-LOW",
        "created_at": "2026-11-23T10:00:00Z",
        "risk_level": "LOW",
        "risk_score": 0,
        "input_type": "url",
        "category": "genuine_service",
        "subject": "Verified SBI Official Portal",
        "raw_content": "https://www.sbi.co.in",
        "content_sha256": "abc123low",
        "indicators": [],
        "identifiers": [{"type": "domain", "value": "sbi.co.in"}],
        "safety_recommendations": get_safety_recommendations("LOW"),
        "is_demo": False
    }
    low_pdf = generate_case_pdf_report(low_case)
    assert low_pdf is not None
    assert len(low_pdf) > 1000

    high_case = {
        "case_id": "CASE-TEST-HIGH",
        "created_at": "2026-11-23T10:00:00Z",
        "risk_level": "HIGH",
        "risk_score": 85,
        "input_type": "url",
        "category": "phishing_link",
        "subject": "Fake SBI KYC Portal",
        "raw_content": "http://sbi-kyc-update.xyz/login",
        "content_sha256": "abc123high",
        "indicators": [{"name": "Suspicious TLD", "points": 25, "explanation": "Domain uses .xyz"}],
        "identifiers": [{"type": "domain", "value": "sbi-kyc-update.xyz"}],
        "safety_recommendations": get_safety_recommendations("HIGH"),
        "is_demo": False
    }
    high_pdf = generate_case_pdf_report(high_case)
    assert high_pdf is not None
    assert len(high_pdf) > 1000
