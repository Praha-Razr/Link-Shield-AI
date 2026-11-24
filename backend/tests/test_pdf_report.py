import pytest
import pypdfium2 as pdfium
from app.reports.pdf import generate_case_pdf_report, FONT_NAME, DEV_FONT_NAME

def test_pdf_fonts_registered():
    """Confirms bundled NotoSans (Latin) and NotoSansDevanagari fonts are loaded without Windows dependencies."""
    assert FONT_NAME == "NotoSans", f"Expected default FONT_NAME to be 'NotoSans', got '{FONT_NAME}'"
    assert DEV_FONT_NAME == "NotoSansDevanagari", f"Expected DEV_FONT_NAME to be 'NotoSansDevanagari', got '{DEV_FONT_NAME}'"

@pytest.mark.parametrize("case_payload,expected_tokens", [
    (
        {
            "id": "ENG-TEST",
            "subject": "Urgent Part-Time Job Offer with High Daily Returns",
            "input_type": "message",
            "risk_score": 85,
            "risk_level": "HIGH",
            "category": "job_scam",
            "status": "open",
            "is_demo": False,
            "raw_content": "Dear candidate, you have been selected for task rating job. Earn Rs 5000 daily from home. Join Telegram group.",
            "content_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "investigator_notes": "Telegram rating task fraud syndicate operating out of state borders.",
            "indicators": [
                {"name": "Unrealistic Daily Earnings Promise", "points": 35, "explanation": "Promises Rs 5000 daily payout with no prior experience."}
            ],
            "identifiers": [
                {"type": "phone", "value": "+91 9876543210"},
                {"type": "telegram", "value": "@TaskJobDaily"}
            ]
        },
        ["LINKSHIELD AI", "Risk", "Indicators", "Unrealistic Daily Earnings", "Candidate", "HIGH RISK", "@TaskJobDaily"]
    ),
    (
        {
            "id": "HI-TEST",
            "subject": "बिजली बिल डिस्कनेक्शन चेतावनी - तत्काल भुगतान सूचना",
            "input_type": "message",
            "risk_score": 90,
            "risk_level": "HIGH",
            "category": "electricity_scam",
            "status": "open",
            "is_demo": True,
            "raw_content": "प्रिय उपभोक्ता, आपका बिजली कनेक्शन आज रात 9:30 बजे काट दिया जाएगा क्योंकि पिछले माह का बिल अपडेट नहीं हुआ है। तुरंत संपर्क करें।",
            "content_sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
            "investigator_notes": "बिजली बिल फ्रॉड सिंडिकेट - खाता फ्रीज करने की सिफारिश।",
            "indicators": [
                {"name": "अति आवश्यक डिस्कनेक्शन धमकी (Urgent Threat)", "points": 40, "explanation": "उपभोक्ता को बिजली आपूर्ति बाधित करने की तात्कालिक धमकी।"}
            ],
            "identifiers": [
                {"type": "phone", "value": "+91 9123456789"}
            ]
        },
        ["LINKSHIELD AI", "Risk", "Indicators", "बिजली", "डिस्कनेक्शन", "उपभोक्ता", "चेतावनी", "HIGH RISK"]
    ),
    (
        {
            "id": "MIX-TEST",
            "subject": "SBI YONO Account Deactivation Alert - तुरंत KYC वेरिफिकेशन करें",
            "input_type": "message",
            "risk_score": 85,
            "risk_level": "HIGH",
            "category": "banking_fraud",
            "status": "active",
            "is_demo": False,
            "raw_content": "Dear Customer, your State Bank of India YONO account is suspended. कृपया 24 घंटे के भीतर पैन कार्ड लिंक करें: http://sbi-kyc-verify.test",
            "content_sha256": "ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d",
            "investigator_notes": "Bank phishing kit targeting SBI account holders. Pan-Aadhaar linking lures. फर्जी वेबसाइट डोमेन दर्ज।",
            "indicators": [
                {"name": "SBI Brand Impersonation (ब्रांड धोखाधड़ी)", "points": 35, "explanation": "अनधिकृत डोमेन द्वारा भारतीय स्टेट बैंक का प्रतिरूपण।"}
            ],
            "identifiers": [
                {"type": "domain", "value": "sbi-kyc-verify.test"},
                {"type": "bank", "value": "State Bank of India"}
            ]
        },
        ["LINKSHIELD AI", "Risk", "Indicators", "SBI YONO", "State Bank", "वेरिफिकेशन", "धोखाधड़ी", "HIGH RISK"]
    ),
    (
        {
            "id": "URL-TEST",
            "subject": "Phishing URL Targeting Banking Portal",
            "input_type": "url",
            "risk_score": 75,
            "risk_level": "HIGH",
            "category": "phishing",
            "status": "open",
            "is_demo": False,
            "raw_content": "https://secure-hdfc-update-portal.test/login.php?client_id=987123",
            "content_sha256": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
            "investigator_notes": "Domain registered recently. Typosquatting brand name HDFC Bank.",
            "indicators": [
                {"name": "Typosquatting Brand Impersonation", "points": 35, "explanation": "Domain closely resembles official banking domain."}
            ],
            "identifiers": [
                {"type": "domain", "value": "secure-hdfc-update-portal.test"},
                {"type": "url", "value": "https://secure-hdfc-update-portal.test/login.php?client_id=987123"}
            ]
        },
        ["LINKSHIELD AI", "Risk", "Indicators", "secure-hdfc-update-portal.test", "Typosquatting", "HIGH RISK"]
    ),
    (
        {
            "id": "WEB-TEST",
            "subject": "Illegal Online Betting & Casino Website",
            "input_type": "website",
            "risk_score": 80,
            "risk_level": "HIGH",
            "category": "illegal_betting",
            "status": "flagged",
            "is_demo": False,
            "raw_content": "<html><title>IPL Win 100x Daily</title><body>Deposit 1000 get 10000 bonus. UPI pay: bettingking@okaxis</body></html>",
            "content_sha256": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
            "investigator_notes": "Mule UPI account bettingking@okaxis detected. Multiple complaints linked.",
            "indicators": [
                {"name": "Unlicensed Financial Gambling Gateway", "points": 40, "explanation": "Illegal peer-to-peer betting UPI collection mechanism."}
            ],
            "identifiers": [
                {"type": "upi", "value": "bettingking@okaxis"}
            ]
        },
        ["LINKSHIELD AI", "Risk", "Indicators", "bettingking@okaxis", "Gambling Gateway", "HIGH RISK"]
    ),
    (
        {
            "id": "SPEC-TEST",
            "subject": "Loan Scam with <b> & \"quotes\" & 'apostrophes' <script>alert(1)</script>",
            "input_type": "message",
            "risk_score": 70,
            "risk_level": "HIGH",
            "category": "loan_fraud",
            "status": "open",
            "is_demo": False,
            "raw_content": "Special offer: Instant loan approved for <Amount> & 'bonus' at \"zero percent\" interest! Click: <b>http://scam.test/apply</b>",
            "content_sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
            "investigator_notes": "Payload tests XML escaping and quote handling in ReportLab paragraphs.",
            "indicators": [
                {"name": "Zero-Interest Instant Loan Trap", "points": 35, "explanation": "Offers <instant> loan & upfront fee request."}
            ],
            "identifiers": [
                {"type": "url", "value": "http://scam.test/apply"}
            ]
        },
        ["LINKSHIELD AI", "Risk", "Indicators", "quotes", "zero percent", "Instant loan", "HIGH RISK"]
    )
])
def test_pdf_report_rendering_and_text_extraction(case_payload, expected_tokens):
    """Generates PDF, extracts text, and asserts presence of Latin & Devanagari words."""
    pdf_bytes = generate_case_pdf_report(case_payload)
    assert len(pdf_bytes) > 5000, "PDF byte stream unexpectedly small"
    assert pdf_bytes.startswith(b"%PDF"), "Output is not a valid PDF document"

    # Extract text using pypdfium2
    doc = pdfium.PdfDocument(pdf_bytes)
    assert len(doc) >= 1, "PDF document has no pages"

    full_text = ""
    for page in doc:
        full_text += page.get_textpage().get_text_range() + "\n"

    # Normalize whitespace for multi-line wrapped table cells
    normalized_text = " ".join(full_text.split())

    for token in expected_tokens:
        assert token.lower() in normalized_text.lower(), (
            f"Expected token '{token}' not found in extracted PDF text for case {case_payload['id']}!\n"
            f"Extracted Text:\n{normalized_text[:400]}..."
        )

    # Verify rendering to image succeeds without glyph/rendering errors
    img = doc[0].render(scale=1.5).to_pil()
    assert img.size[0] > 0 and img.size[1] > 0
