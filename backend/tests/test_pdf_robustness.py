import pytest
from app.reports.pdf import generate_case_pdf_report, safe_text, wrap_unbroken_words

def test_safe_text_and_wrapping():
    # Long unbroken string
    long_str = "A" * 200
    wrapped = wrap_unbroken_words(long_str, max_word_len=50)
    assert len(wrapped) > 200
    assert " " in wrapped

    # HTML and XML special characters
    xss = "<script>alert('xss & attack')</script>"
    escaped = safe_text(xss)
    assert "<script>" not in escaped
    assert "&lt;script&gt;" in escaped
    assert "&amp;" in escaped

    # None and empty
    assert safe_text(None) == ""
    assert safe_text("") == ""

def test_pdf_generation_6_cases():
    cases = [
        # 1. Message case
        {
            "id": "TEST-MSG-001",
            "subject": "Electricity Bill Suspension Threat",
            "input_type": "message",
            "risk_level": "HIGH",
            "risk_score": 85,
            "category": "utility_fraud",
            "is_demo": False,
            "content_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "raw_content": "Dear consumer your electricity power will be disconnected tonight at 9:30 PM. Call officer at +919876543210 immediately.",
            "indicators": [
                {"name": "Urgency / Threat", "points": 30, "explanation": "Demands immediate compliance"},
                {"name": "Suspicious Contact Phone", "points": 25, "explanation": "Personal phone number instead of official IVR"}
            ],
            "identifiers": [
                {"type": "phone", "value": "+919876543210"}
            ],
            "related_cases": [],
            "similarity_links": [],
            "investigator_notes": "Identified as part of statewide power cut scam wave."
        },
        # 2. URL case
        {
            "id": "TEST-URL-002",
            "subject": "Fake SBI KYC Phishing Portal",
            "input_type": "url",
            "risk_level": "HIGH",
            "risk_score": 90,
            "category": "phishing",
            "is_demo": False,
            "content_sha256": "8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4",
            "raw_content": "http://sbi-kyc-pan-update.com/login?ref=sms_link",
            "indicators": [
                {"name": "Brand Impersonation: SBI", "points": 40, "explanation": "Domain imitates State Bank of India"},
                {"name": "Credential Harvesting Pattern", "points": 30, "explanation": "Directs to mock banking login"}
            ],
            "identifiers": [
                {"type": "domain", "value": "sbi-kyc-pan-update.com"},
                {"type": "url", "value": "http://sbi-kyc-pan-update.com/login"}
            ],
            "related_cases": [],
            "similarity_links": [],
            "investigator_notes": "Notice sent to registrar for emergency suspension."
        },
        # 3. Website case
        {
            "id": "TEST-WEB-003",
            "subject": "Apex Multiplier Ponzi Investment Web Page",
            "input_type": "website",
            "risk_level": "HIGH",
            "risk_score": 80,
            "category": "fake_investment",
            "is_demo": False,
            "content_sha256": "5c9b0e9a3b689a9f4e427d143c683b77be3db53a7b1b36bc932a3f7ff9e49fb0",
            "raw_content": "<html><body><h1>Double your money in 48 hours</h1><p>Deposit USDT to TRX wallet: TTestWalletAddressCaseSensitive123</p></body></html>",
            "indicators": [
                {"name": "Guaranteed Returns / Ponzi", "points": 35, "explanation": "Claims 100% ROI in 48 hours"},
                {"name": "Direct Crypto Deposit", "points": 25, "explanation": "Unregistered wallet collection"}
            ],
            "identifiers": [
                {"type": "crypto_wallet", "value": "TTestWalletAddressCaseSensitive123"}
            ],
            "related_cases": [],
            "similarity_links": [],
            "investigator_notes": "Website claims SEBI registration which was proven fake."
        },
        # 4. Hindi / Devanagari case
        {
            "id": "TEST-HIN-004",
            "subject": "बिजली बिल डिस्कनेक्शन नोटिस एवं बैंक लॉटरी धोखाधड़ी",
            "input_type": "message",
            "risk_level": "HIGH",
            "risk_score": 85,
            "category": "utility_fraud",
            "is_demo": False,
            "content_sha256": "11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
            "raw_content": "प्रिय ग्राहक, आपका बिजली बिल बकाया है। यदि तुरंत भुगतान नहीं किया गया तो आज रात 9:30 बजे बिजली काट दी जाएगी। संपर्क: 9000000001",
            "indicators": [
                {"name": "Urgent Disconnection Notice (Hindi)", "points": 35, "explanation": "हिंदी में तत्काल बिजली काटने की फर्जी चेतावनी"},
                {"name": "Suspicious Mobile Number", "points": 25, "explanation": "फर्जी अधिकारी का मोबाइल नंबर"}
            ],
            "identifiers": [
                {"type": "phone", "value": "+919000000001"}
            ],
            "related_cases": [],
            "similarity_links": [],
            "investigator_notes": "प्रकरण में साइबर थाना जयपुर को शिकायत प्रेषित की गई।"
        },
        # 5. Demo case (with DEMO watermark)
        {
            "id": "DEMO-001",
            "subject": "DEMO: Synthetic Evaluation Record - Instant Loan Fraud",
            "input_type": "message",
            "risk_level": "MEDIUM",
            "risk_score": 45,
            "category": "fake_loan",
            "is_demo": True,
            "content_sha256": "abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdef",
            "raw_content": "Congratulations! Instant pre-approved loan of Rs 5,00,000 without CIBIL check. Pay processing fee of Rs 1,999 to demo.pay@demoupi",
            "indicators": [
                {"name": "Upfront Processing Fee", "points": 25, "explanation": "Demands payment before loan disbursement"}
            ],
            "identifiers": [
                {"type": "upi", "value": "demo.pay@demoupi"}
            ],
            "related_cases": [],
            "similarity_links": [],
            "investigator_notes": "Sample evaluation scenario for hackathon demonstration."
        },
        # 6. Special Characters and Extreme Input Case
        {
            "id": "TEST-SPEC-006",
            "subject": "Injection Test: <script>alert('XSS')</script> & 'Quotes' \"Double\" &nbsp; ? = #",
            "input_type": "message",
            "risk_level": "LOW",
            "risk_score": 10,
            "category": "general",
            "is_demo": False,
            "content_sha256": "0000111122223333444455556666777788889999aaaabbbbccccddddeeeeffff",
            # Continuous token without space of 3000 chars + special xml characters + null byte
            "raw_content": "Dangerous payload: <xml><node attr='val&test'>Hello</node></xml>\x00 " + ("Z" * 1500) + " " + ("X" * 1500),
            "indicators": [
                {"name": "XSS & XML Tag Check <tag>", "points": 5, "explanation": "Contains raw HTML tags & quotes: \" ' < > &"}
            ],
            "identifiers": [
                {"type": "domain", "value": "test-domain&check.com"}
            ],
            "related_cases": [],
            "similarity_links": [],
            "investigator_notes": "Special character stress test notes with <p>markup</p> and & special entities."
        }
    ]

    for c in cases:
        pdf_bytes = generate_case_pdf_report(c)
        assert pdf_bytes is not None, f"PDF bytes should not be None for {c['id']}"
        assert pdf_bytes.startswith(b"%PDF-"), f"PDF for {c['id']} does not start with %PDF-"
        assert len(pdf_bytes) > 1000, f"PDF for {c['id']} is too small ({len(pdf_bytes)} bytes)"

def test_pdf_endpoint_via_client(client):
    # 1. Post a test message
    post_res = client.post("/api/analyze/message", json={
        "content": "Urgent: Your SBI account is blocked. Visit http://sbi-unblock.test/verify to resume services.",
        "subject": "SBI Block Test"
    })
    assert post_res.status_code == 200
    case_id = post_res.json()["case_id"]

    # 2. Fetch PDF
    pdf_res = client.get(f"/api/reports/{case_id}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["Content-Type"] == "application/pdf"
    assert f"LinkShield_Report_{case_id}.pdf" in pdf_res.headers["Content-Disposition"]
    assert pdf_res.content.startswith(b"%PDF-")
    assert len(pdf_res.content) > 1000
