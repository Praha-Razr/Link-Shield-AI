from app.analyzers.message import analyze_message_content

def test_unseen_dataset_classification():
    """
    Tests 5 NEW unseen scam messages and 5 NEW unseen genuine messages
    that were NOT used when tuning the indicators or rules.
    Verifies that all 10 are classified correctly.
    """
    unseen_scam_samples = [
        {
            "id": "UNSEEN-SCAM-1",
            "name": "Personal Loan Phishing Link",
            "text": "Your SBI instant paperless personal loan of Rs 2,50,000 has been approved at 4.5% interest. Click to accept and verify documents: http://sbi-personal-loan-instant.test"
        },
        {
            "id": "UNSEEN-SCAM-2",
            "name": "Hinglish Electricity Disconnection",
            "text": "Bijli bill update: Priya upbhokta, aapka bijli connection aaj raat 9:30 baje cut ho jayega. Bill jama nahi kiya hai. Turant sampark karein +91 90000 00028."
        },
        {
            "id": "UNSEEN-SCAM-3",
            "name": "Customs Duty Advance Payment",
            "text": "Consignment notification: Your foreign parcel is detained at Mumbai customs clearance due to unpaid duty. Pay refundable deposit of Rs 1,499 to UPI customs.duty@demoupi to release immediately."
        },
        {
            "id": "UNSEEN-SCAM-4",
            "name": "Cryptocurrency High-Yield Ponzi",
            "text": "Exclusive Crypto Pool: Double your money in 24 hours! 100% risk free guaranteed return on every investment. Deposit funds to TRON address TLyqzVGLV1srkB7dToTAwdg296wc9g32pU."
        },
        {
            "id": "UNSEEN-SCAM-5",
            "name": "Hinglish KYC Account Suspension",
            "text": "Kotak Bank alert: Your netbanking will be suspended within 24 hours due to unverified PAN details. Submit documents immediately at http://demo-scam.test/kotak-kyc or your khata band ho jayega."
        }
    ]

    unseen_genuine_samples = [
        {
            "id": "UNSEEN-GENUINE-1",
            "name": "Bank ATM Withdrawal Alert",
            "text": "Dear Customer, INR 2,150.00 withdrawn from ATM at Jaipur Branch on 22-Nov-2026. Account balance: INR 43,100.20. Punjab National Bank."
        },
        {
            "id": "UNSEEN-GENUINE-2",
            "name": "IRCTC Train Status Update",
            "text": "IRCTC update: Train 12956 (Jaipur Superfast Express) is on time from destination on 23-Nov-2026. Coach B2, Seat 45 (Confirmed). Have a pleasant trip."
        },
        {
            "id": "UNSEEN-GENUINE-3",
            "name": "Pathology Lab Report Notification",
            "text": "Your blood test diagnostic report (Ref #L-99812) is ready for collection at Central Pathology Lab. You may also view it on the registered patient portal."
        },
        {
            "id": "UNSEEN-GENUINE-4",
            "name": "Corporate Salary Credit Alert",
            "text": "Salary for the month of November 2026 has been successfully credited to your bank account ending in 4102. Net amount: Rs 64,500.00. Finance Dept."
        },
        {
            "id": "UNSEEN-GENUINE-5",
            "name": "Courier Out for Delivery Notice",
            "text": "Hi, our courier associate Rajesh is out for delivery with your shipment #PK99218. Delivery will be attempted by 5:00 PM today. No action required."
        }
    ]

    correct_scams = 0
    correct_genuine = 0

    print("\n--- Evaluating 5 Unseen Scam Messages ---")
    for sample in unseen_scam_samples:
        result = analyze_message_content(sample["text"])
        risk = result["risk_level"]
        score = result["risk_score"]
        print(f"[{sample['id']}] {sample['name']} -> {risk} ({score} pts), Category: {result['category']}")
        assert risk in ("MEDIUM", "HIGH"), f"{sample['id']} scored {risk} ({score} pts), expected MEDIUM/HIGH"
        correct_scams += 1

    print("\n--- Evaluating 5 Unseen Genuine Messages ---")
    for sample in unseen_genuine_samples:
        result = analyze_message_content(sample["text"])
        risk = result["risk_level"]
        score = result["risk_score"]
        print(f"[{sample['id']}] {sample['name']} -> {risk} ({score} pts), Category: {result['category']}")
        assert risk == "LOW", f"{sample['id']} scored {risk} ({score} pts), expected LOW"
        correct_genuine += 1

    assert correct_scams == 5
    assert correct_genuine == 5
    print(f"\nUnseen Evaluation Result: {correct_scams}/5 scams and {correct_genuine}/5 genuine correctly classified (10/10 total)")
