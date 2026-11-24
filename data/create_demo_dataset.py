import json
from pathlib import Path

data_dir = Path(__file__).resolve().parent
dataset_path = data_dir / "demo_dataset.json"

records = []

# --- 10 Genuine Messages (GENUINE, LOW RISK) ---
genuine_messages = [
    {
        "case_id": "DEMO-001",
        "category": "genuine_service",
        "input_type": "message",
        "submitted_content": "Your a/c no. XX9921 is credited with INR 5,000 on 22-Nov-2026. Ref: TXN998877. State Bank of India.",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": ["Legitimate Transactional Alert Pattern"],
        "expected_identifiers": ["domain:sbi.co.in", "bank_account:XX9921"]
    },
    {
        "case_id": "DEMO-002",
        "category": "genuine_service",
        "input_type": "message",
        "submitted_content": "Your OTP for login to your personal service portal is 482910. Do not share this OTP with anyone. Valid for 10 minutes.",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": ["Legitimate Transactional Alert Pattern"],
        "expected_identifiers": []
    },
    {
        "case_id": "DEMO-003",
        "category": "genuine_service",
        "input_type": "message",
        "submitted_content": "Your shipment #TRK9921 from National Logistics is out for delivery today. Delivery agent will contact you shortly.",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": ["Legitimate Transactional Alert Pattern"],
        "expected_identifiers": []
    },
    {
        "case_id": "DEMO-004",
        "category": "genuine_service",
        "input_type": "message",
        "submitted_content": "Dear Candidate, Your interview for Junior Analyst is scheduled on 28-Nov-2026 at 10:30 AM via corporate portal. Team HR.",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": ["Legitimate Transactional Alert Pattern"],
        "expected_identifiers": []
    },
    {
        "case_id": "DEMO-005",
        "category": "genuine_service",
        "input_type": "message",
        "submitted_content": "Bill payment received successfully. Amount Rs 1,450 credited against electricity consumer ID 982100123. Thank you for your payment.",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": ["Legitimate Transactional Alert Pattern"],
        "expected_identifiers": []
    },
    {
        "case_id": "DEMO-006",
        "category": "genuine_service",
        "input_type": "message",
        "submitted_content": "Ticket confirmed: PNR 8A99K2. Flight SG-201 from DEL to JAI on 25-Nov. Have a safe journey with SpiceJet.",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": ["Legitimate Transactional Alert Pattern"],
        "expected_identifiers": []
    },
    {
        "case_id": "DEMO-007",
        "category": "genuine_service",
        "input_type": "message",
        "submitted_content": "Your appointment with Dr. Sharma is confirmed for tomorrow 11:00 AM at City Clinic. Please arrive 15 minutes early.",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": [],
        "expected_identifiers": []
    },
    {
        "case_id": "DEMO-008",
        "category": "genuine_service",
        "input_type": "message",
        "submitted_content": "Notice: Semester examination timetable is released on student portal. Exams commence from 15th December 2026.",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": [],
        "expected_identifiers": []
    },
    {
        "case_id": "DEMO-009",
        "category": "genuine_service",
        "input_type": "message",
        "submitted_content": "Dear customer, your monthly broadband plan has been renewed successfully. Next billing date: 22-Dec-2026.",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": ["Legitimate Transactional Alert Pattern"],
        "expected_identifiers": []
    },
    {
        "case_id": "DEMO-010",
        "category": "genuine_service",
        "input_type": "message",
        "submitted_content": "Order #88219 has been packed and handed over to our delivery partner. Estimated arrival in 30 minutes. Thank you.",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": [],
        "expected_identifiers": []
    }
]
records.extend(genuine_messages)

# --- 10 Suspicious Messages (SCAM, MEDIUM or HIGH) ---
suspicious_messages = [
    {
        "case_id": "DEMO-011",
        "category": "fake_kyc",
        "input_type": "message",
        "submitted_content": "URGENT NOTICE: Your SBI account has been suspended immediately due to pending KYC verification. Update KYC within 24 hours at http://demo-scam.test/kyc or your account will be blocked today. Contact officer at +91 90000 00001.",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Fake KYC or Account-Block Warning", "Urgency or Threatening Language", "Institutional or Brand Impersonation"],
        "expected_identifiers": ["phone:+919000000001", "url:http://demo-scam.test/kyc", "domain:demo-scam.test"]
    },
    {
        "case_id": "DEMO-012",
        "category": "electricity_scam",
        "input_type": "message",
        "submitted_content": "Dear consumer, your electricity power will be disconnected tonight at 9:30 pm from electricity office because your bill unpaid. Please contact electricity officer at +91 90000 00002 immediately.",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Electricity Disconnection Scam Pattern", "Urgency or Threatening Language"],
        "expected_identifiers": ["phone:+919000000002"]
    },
    {
        "case_id": "DEMO-013",
        "category": "parcel_scam",
        "input_type": "message",
        "submitted_content": "India Post Alert: Package cannot be delivered because delivery address incorrect. Pay unpaid customs fee of Rs 48 within 24 hours to reschedule delivery: http://indiapost-parcel-fee.test",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Parcel Delivery or Customs Fee Scam", "Institutional or Brand Impersonation", "Urgency or Threatening Language"],
        "expected_identifiers": ["url:http://indiapost-parcel-fee.test", "domain:indiapost-parcel-fee.test"]
    },
    {
        "case_id": "DEMO-014",
        "category": "job_fraud",
        "input_type": "message",
        "submitted_content": "Part time job opportunity: Work from home daily earning Rs 2000 to 5000 per day by youtube like video earn. Daily payout guaranteed. Pay registration fee to upi demo.pay@demoupi to activate task.",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Fake Work-From-Home or Task Job", "Suspicious Direct Payment Request"],
        "expected_identifiers": ["upi:demo.pay@demoupi"]
    },
    {
        "case_id": "DEMO-015",
        "category": "fake_kyc",
        "input_type": "message",
        "submitted_content": "HDFC Bank Alert: Last warning. Your bank a/c will be blocked today due to PAN card not linked. Send payment to upi hdfc.verify@demoupi or call +91 90000 00003 immediately.",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Fake KYC or Account-Block Warning", "Institutional or Brand Impersonation", "Urgency or Threatening Language"],
        "expected_identifiers": ["upi:hdfc.verify@demoupi", "phone:+919000000003"]
    },
    {
        "case_id": "DEMO-016",
        "category": "loan_fraud",
        "input_type": "message",
        "submitted_content": "Instant loan approved! Pre-approved loan of Rs 5,00,000 with no cibil required and no document loan. Pay processing fee to account 987654321098 IFSC SBIN0001234.",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Unverified Instant Loan Claim", "Suspicious Direct Payment Request"],
        "expected_identifiers": ["bank_account:987654321098", "bank_account:IFSC:SBIN0001234"]
    },
    {
        "case_id": "DEMO-017",
        "category": "fake_kyc",
        "input_type": "message",
        "submitted_content": "अंतिम चेतावनी: आपका बैंक खाता बंद कर दिया जाएगा। तुरंत केवाईसी अपडेट करें। आधार कार्ड सत्यापन हेतु तुरंत संपर्क करें +91 90000 00004।",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Fake KYC or Account-Block Warning", "Urgency or Threatening Language"],
        "expected_identifiers": ["phone:+919000000004"]
    },
    {
        "case_id": "DEMO-018",
        "category": "electricity_scam",
        "input_type": "message",
        "submitted_content": "प्रिय उपभोक्ता, बिजली विभाग: आपका बिजली का बिल बकाया है। आज रात ९:३० बजे बिजली काट दी जाएगी। तुरंत अधिकारी से संपर्क करें +91 90000 00005।",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Electricity Disconnection Scam Pattern", "Urgency or Threatening Language"],
        "expected_identifiers": ["phone:+919000000005"]
    },
    {
        "case_id": "DEMO-019",
        "category": "job_fraud",
        "input_type": "message",
        "submitted_content": "Urgent part time job offer: Ghar baithe kamaye 3000 per day. Task complete karein aur paise transfer karein. Registration charge ke liye UPI par bhejo: job.verify@demoupi.",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Fake Work-From-Home or Task Job", "Suspicious Direct Payment Request"],
        "expected_identifiers": ["upi:job.verify@demoupi"]
    },
    {
        "case_id": "DEMO-020",
        "category": "fake_kyc",
        "input_type": "message",
        "submitted_content": "Aapka account block ho jayega aaj raat tak! Turant KYC update karein nahi to khata band ho jayega. Final warning. Contact +91 90000 00006.",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Fake KYC or Account-Block Warning", "Urgency or Threatening Language"],
        "expected_identifiers": ["phone:+919000000006"]
    }
]
records.extend(suspicious_messages)

# --- 10 Suspicious URLs (SCAM, MEDIUM or HIGH) ---
suspicious_urls = [
    {
        "case_id": "DEMO-021",
        "category": "phishing_link",
        "input_type": "url",
        "submitted_content": "http://sbi-netbanking-kyc-verify.test/login",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Look-alike Brand Domain", "Suspicious URL Structure Pattern", "Unencrypted HTTP Scheme"],
        "expected_identifiers": ["domain:sbi-netbanking-kyc-verify.test"]
    },
    {
        "case_id": "DEMO-022",
        "category": "phishing_link",
        "input_type": "url",
        "submitted_content": "http://hdfcbank-security-update.test/portal/login",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Look-alike Brand Domain", "Suspicious URL Structure Pattern", "Unencrypted HTTP Scheme"],
        "expected_identifiers": ["domain:hdfcbank-security-update.test"]
    },
    {
        "case_id": "DEMO-023",
        "category": "phishing_link",
        "input_type": "url",
        "submitted_content": "http://198.51.100.23/online-banking/verify",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Suspicious URL Structure Pattern", "Unencrypted HTTP Scheme"],
        "expected_identifiers": ["domain:198.51.100.23"]
    },
    {
        "case_id": "DEMO-024",
        "category": "phishing_link",
        "input_type": "url",
        "submitted_content": "http://xn--sb-1ia.test/account-update",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Suspicious URL Structure Pattern", "Unencrypted HTTP Scheme"],
        "expected_identifiers": ["domain:xn--sb-1ia.test"]
    },
    {
        "case_id": "DEMO-025",
        "category": "blacklisted_domain",
        "input_type": "url",
        "submitted_content": "http://demo-scam.test/secure-login",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Known Blacklisted Domain", "Suspicious URL Structure Pattern", "Unencrypted HTTP Scheme"],
        "expected_identifiers": ["domain:demo-scam.test"]
    },
    {
        "case_id": "DEMO-026",
        "category": "loan_fraud",
        "input_type": "url",
        "submitted_content": "http://free-instant-loan.test/apply",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Known Blacklisted Domain", "Unverified Instant Loan Claim", "Unencrypted HTTP Scheme"],
        "expected_identifiers": ["domain:free-instant-loan.test"]
    },
    {
        "case_id": "DEMO-027",
        "category": "investment_fraud",
        "input_type": "url",
        "submitted_content": "http://crypto-double-returns.test/invest",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Known Blacklisted Domain", "High-Multiplier or Double Money Scheme", "Unencrypted HTTP Scheme"],
        "expected_identifiers": ["domain:crypto-double-returns.test"]
    },
    {
        "case_id": "DEMO-028",
        "category": "phishing_link",
        "input_type": "url",
        "submitted_content": "http://secure.login.verify.update.banking.demo-scam.test/",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Known Blacklisted Domain", "Suspicious URL Structure Pattern", "Unencrypted HTTP Scheme"],
        "expected_identifiers": ["domain:secure.login.verify.update.banking.demo-scam.test"]
    },
    {
        "case_id": "DEMO-029",
        "category": "phishing_link",
        "input_type": "url",
        "submitted_content": "http://indiapost-customs-clearance.test/track",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Look-alike Brand Domain", "Suspicious URL Structure Pattern", "Unencrypted HTTP Scheme"],
        "expected_identifiers": ["domain:indiapost-customs-clearance.test"]
    },
    {
        "case_id": "DEMO-030",
        "category": "phishing_link",
        "input_type": "url",
        "submitted_content": "http://quick-bonus-claim-reward.xyz/payout",
        "expected_classification": "scam",
        "expected_risk_level": "MEDIUM",
        "relevant_indicators": ["Suspicious URL Structure Pattern", "Unencrypted HTTP Scheme"],
        "expected_identifiers": ["domain:quick-bonus-claim-reward.xyz"]
    }
]
records.extend(suspicious_urls)

# --- 10 Website Samples as HTML Strings ---
website_samples = [
    # 2 Genuine info pages
    {
        "case_id": "DEMO-031",
        "category": "genuine_service",
        "input_type": "website",
        "submitted_content": """<!DOCTYPE html>
<html>
<head><title>National Financial Literacy Guide</title></head>
<body>
  <h1>Personal Budgeting & Financial Awareness</h1>
  <p>Learn how to manage personal savings, understand bank interest calculations, and protect yourself against cyber scams.</p>
  <p>Never share your passwords or OTPs with unknown individuals. Verify official bank communications.</p>
</body>
</html>""",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": [],
        "expected_identifiers": []
    },
    {
        "case_id": "DEMO-032",
        "category": "genuine_service",
        "input_type": "website",
        "submitted_content": """<!DOCTYPE html>
<html>
<head><title>Cyber Safety Advisory - Citizen Portal</title></head>
<body>
  <h1>Cyber Crime Awareness & Prevention Cell</h1>
  <p>Rajasthan Police advises all citizens to stay alert against phishing links and fake call centers.</p>
  <p>For reporting cyber fraud, dial national helpline 1930 or submit details on cybercrime.gov.in.</p>
</body>
</html>""",
        "expected_classification": "genuine",
        "expected_risk_level": "LOW",
        "relevant_indicators": [],
        "expected_identifiers": []
    },
    # 3 Fake investment websites
    {
        "case_id": "DEMO-033",
        "category": "investment_fraud",
        "input_type": "website",
        "submitted_content": """<!DOCTYPE html>
<html>
<head><title>Apex Crypto Wealth - Guaranteed Profit</title></head>
<body>
  <h1>100% Risk Free Guaranteed Return Trading</h1>
  <p>Earn fixed monthly profit with our automated AI crypto trading algorithms. Guaranteed return on every deposit.</p>
  <p>Deposit funds to our official Bitcoin wallet address: 1SyntheticBtcFakeAddressForDemo99</p>
  <a href="tel:+919000000008">Call Support Desk</a>
</body>
</html>""",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Guaranteed Return Investment Claims", "Suspicious Website Payment Request"],
        "expected_identifiers": ["crypto_wallet:1SyntheticBtcFakeAddressForDemo99", "phone:+919000000008"]
    },
    {
        "case_id": "DEMO-034",
        "category": "investment_fraud",
        "input_type": "website",
        "submitted_content": """<!DOCTYPE html>
<html>
<head><title>Global Forex Yield - Assured Returns</title></head>
<body>
  <h1>Assured Returns High Yield Investment Program</h1>
  <p>Guaranteed profit every 24 hours with zero risk investment packages.</p>
  <p>Send payment to upi invest.profit@demoupi or transfer to account 112233445566 IFSC HDFC0001234.</p>
</body>
</html>""",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Guaranteed Return Investment Claims", "Suspicious Direct Payment Request", "Suspicious Website Payment Request"],
        "expected_identifiers": ["upi:invest.profit@demoupi", "bank_account:112233445566", "bank_account:IFSC:HDFC0001234"]
    },
    {
        "case_id": "DEMO-035",
        "category": "investment_fraud",
        "input_type": "website",
        "submitted_content": """<!DOCTYPE html>
<html>
<head><title>Fixed Profit Robo Trader</title></head>
<body>
  <h1>Automated Fixed Monthly Profit Platform</h1>
  <p>Invest capital and get guaranteed returns every month without market fluctuations.</p>
  <p>Transfer funds to UPI handle trader.deposit@demoupi to begin instant trade activation.</p>
  <a href="mailto:support@investment-scam.test">Contact Support</a>
</body>
</html>""",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Guaranteed Return Investment Claims", "Suspicious Website Payment Request"],
        "expected_identifiers": ["upi:trader.deposit@demoupi", "email:support@investment-scam.test"]
    },
    # 2 Ponzi-style websites
    {
        "case_id": "DEMO-036",
        "category": "investment_fraud",
        "input_type": "website",
        "submitted_content": """<!DOCTYPE html>
<html>
<head><title>Double Wealth Portal</title></head>
<body>
  <h1>Double Your Money in 24 Hours!</h1>
  <p>Instant doubling scheme: invest 1000 get 10000 back today only! Money doubler with 3x returns.</p>
  <p>Deposit funds to upi demo.pay@demoupi and send screenshot on WhatsApp +91 90000 00001.</p>
</body>
</html>""",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["High-Multiplier or Double Money Scheme", "Suspicious Direct Payment Request", "Suspicious Website Payment Request"],
        "expected_identifiers": ["upi:demo.pay@demoupi", "phone:+919000000001"]
    },
    {
        "case_id": "DEMO-037",
        "category": "investment_fraud",
        "input_type": "website",
        "submitted_content": """<!DOCTYPE html>
<html>
<head><title>Fast Multiplier Matrix</title></head>
<body>
  <h1>2x in 24 hours Wealth Multiplier</h1>
  <p>Multiply wealth instantly with our community pool. Double your money guaranteed.</p>
  <p>Send TRON deposit to address: TLyqzVGLV1srkB7dToTAwdg296wc9g32pU</p>
</body>
</html>""",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["High-Multiplier or Double Money Scheme", "Suspicious Website Payment Request"],
        "expected_identifiers": ["crypto_wallet:TLyqzVGLV1srkB7dToTAwdg296wc9g32pU"]
    },
    # 1 MLM referral website
    {
        "case_id": "DEMO-038",
        "category": "mlm_fraud",
        "input_type": "website",
        "submitted_content": """<!DOCTYPE html>
<html>
<head><title>Global Network Matrix</title></head>
<body>
  <h1>MLM Chain & Downline Commission Matrix</h1>
  <p>Invite 5 friends earn downline commission! Direct referral reward and referral bonus for every joiner.</p>
  <p>Pay registration charge of Rs 500 to UPI mlm.join@demoupi to activate member tree.</p>
</body>
</html>""",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Multi-Level or Referral Chain Scheme", "Suspicious Direct Payment Request", "Suspicious Website Payment Request"],
        "expected_identifiers": ["upi:mlm.join@demoupi"]
    },
    # 2 Illegal betting websites
    {
        "case_id": "DEMO-039",
        "category": "illegal_betting",
        "input_type": "website",
        "submitted_content": """<!DOCTYPE html>
<html>
<head><title>Royal Cricket Betting Club</title></head>
<body>
  <h1>Cricket Betting ID Online - IPL Match Betting</h1>
  <p>Get instant cricket betting id with instant withdrawal betting. Online casino bonus on first deposit.</p>
  <p>Contact bookie on WhatsApp +91 90000 00007 or pay to UPI bet.book@demoupi.</p>
</body>
</html>""",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Unregulated Betting or Gambling Promotion", "Suspicious Website Payment Request"],
        "expected_identifiers": ["phone:+919000000007", "upi:bet.book@demoupi"]
    },
    {
        "case_id": "DEMO-040",
        "category": "illegal_betting",
        "input_type": "website",
        "submitted_content": """<!DOCTYPE html>
<html>
<head><title>Super Color Prediction Game & Satta</title></head>
<body>
  <h1>Color Prediction Game - Satta Matka Official</h1>
  <p>Play live color prediction game and online casino bonus! Instant 10x payout every 3 minutes.</p>
  <p>Deposit amount to UPI bet.win@demoupi to get gaming coins.</p>
</body>
</html>""",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Unregulated Betting or Gambling Promotion", "Suspicious Website Payment Request"],
        "expected_identifiers": ["upi:bet.win@demoupi"]
    }
]
records.extend(website_samples)

# --- 4 Extra "Link" Records Reusing Identifiers ---
# Purpose: Connect demo-scam.test, +919000000001, and demo.pay@demoupi into rich graph clusters
extra_link_records = [
    {
        "case_id": "DEMO-041",
        "category": "fake_kyc",
        "input_type": "message",
        "submitted_content": "Final Warning: Your banking services are suspended immediately. Visit portal http://demo-scam.test/login to verify KYC or contact support at +91 90000 00001.",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Fake KYC or Account-Block Warning", "Urgency or Threatening Language"],
        "expected_identifiers": ["phone:+919000000001", "url:http://demo-scam.test/login", "domain:demo-scam.test"]
    },
    {
        "case_id": "DEMO-042",
        "category": "phishing_link",
        "input_type": "url",
        "submitted_content": "http://demo-scam.test/payment-gateway",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Known Blacklisted Domain", "Suspicious URL Structure Pattern", "Unencrypted HTTP Scheme"],
        "expected_identifiers": ["domain:demo-scam.test"]
    },
    {
        "case_id": "DEMO-043",
        "category": "job_fraud",
        "input_type": "message",
        "submitted_content": "Part time job approved: Earn 4000 daily payout. To receive tasks, contact coordinator at +91 90000 00001 and pay processing fee to upi demo.pay@demoupi immediately.",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Fake Work-From-Home or Task Job", "Suspicious Direct Payment Request"],
        "expected_identifiers": ["phone:+919000000001", "upi:demo.pay@demoupi"]
    },
    {
        "case_id": "DEMO-044",
        "category": "investment_fraud",
        "input_type": "website",
        "submitted_content": """<!DOCTYPE html>
<html>
<head><title>Central Investment Gateway - Demo Scam Portal</title></head>
<body>
  <h1>Guaranteed Return Investment Portal</h1>
  <p>Hosted on demo-scam.test: 100% risk free guaranteed return on every deposit.</p>
  <p>Pay registration charge to UPI handle demo.pay@demoupi.</p>
  <a href="http://demo-scam.test/help">Help Portal</a>
</body>
</html>""",
        "expected_classification": "scam",
        "expected_risk_level": "HIGH",
        "relevant_indicators": ["Guaranteed Return Investment Claims", "Suspicious Website Payment Request"],
        "expected_identifiers": ["domain:demo-scam.test", "upi:demo.pay@demoupi"]
    }
]
records.extend(extra_link_records)

# Mark all as DEMO DATA
for r in records:
    r["is_demo"] = True

with open(dataset_path, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2, ensure_ascii=False)

print(f"Generated {len(records)} records in {dataset_path}")
