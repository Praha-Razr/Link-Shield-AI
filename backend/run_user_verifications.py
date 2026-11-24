import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def post_json(path, data):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def get_json(path):
    url = f"{BASE_URL}{path}"
    with urllib.request.urlopen(url) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def run():
    print("=" * 60)
    print("STEP 1: Demo Load Twice & Check Duplicates")
    print("=" * 60)
    status1, load1 = post_json("/api/demo/load", {})
    print(f"First Load Result: status={status1}, loaded={load1.get('loaded_count')}, skipped={load1.get('skipped_count')}")
    
    status2, load2 = post_json("/api/demo/load", {})
    print(f"Second Load Result (Idempotency): status={status2}, loaded={load2.get('loaded_count')}, skipped={load2.get('skipped_count')}")
    
    status_stats, stats = get_json("/api/dashboard/stats")
    print(f"Stats after double load: total_cases={stats.get('total_cases')}, demo_cases={stats.get('demo_cases')}")

    print("\n" + "=" * 60)
    print("STEP 2: 5 Fresh Scam Messages & 5 Fresh Genuine Messages")
    print("=" * 60)
    
    scam_messages = [
        {
            "name": "Electricity Cutoff Scam (EN)",
            "subject": "Electricity Bill Threat",
            "content": "URGENT: Your electricity connection will be disconnected tonight at 9:30 pm from electricity office due to unpaid bill of Rs 1,840. Contact electricity officer immediately at +91 90000 00011 or pay via UPI bijli.pay@demoupi."
        },
        {
            "name": "Instant Loan Scam (EN)",
            "subject": "Pre-approved Instant Loan",
            "content": "Pre-approved loan of Rs 3,50,000 credited! Zero document loan with no CIBIL check required. Pay registration fee of Rs 999 to bank account 501002233445 IFSC HDFC0000123 to disburse amount instantly."
        },
        {
            "name": "Task/Job Scam (Hinglish)",
            "subject": "Part Time Job Daily Earning",
            "content": "Part time job opportunity: Ghar baithe kamaye daily 2500 per day by like karke paise kamaye. Task complete karein aur turant daily payment pao. Registration charge ke liye UPI par bhejo: work.daily@demoupi."
        },
        {
            "name": "Postal Delivery Fee Scam (EN)",
            "subject": "India Post Parcel Reschedule",
            "content": "India Post Notice: Your parcel cannot be delivered because address is incomplete. Pay customs clearance fee of Rs 65 immediately within 24 hours at http://demo-scam.test/parcel-reschedule or package will be returned to sender."
        },
        {
            "name": "Bank KYC Block Impersonation (EN)",
            "subject": "SBI Account Deactivation Notice",
            "content": "SBI Alert: Your bank account will be blocked today! Immediate action required within 24 hours: complete KYC verification at http://demo-scam.test/sbi-kyc or contact officer at +91 90000 00012."
        }
    ]

    genuine_messages = [
        {
            "name": "Debit Transaction Alert (EN)",
            "subject": "Bank Debit Alert",
            "content": "Dear customer, Rs 450.00 has been debited from your a/c XX4019 on 22-Nov-2026 19:40 for UPI purchase at Metro Supermarket. Available balance: INR 18,240.50. Bank of Baroda."
        },
        {
            "name": "E-Commerce Delivery Confirmation (EN)",
            "subject": "Order Delivered",
            "content": "Your order #ORD-99124 has been delivered by courier partner. Thank you for shopping with us! Please rate your delivery experience on your registered mobile app."
        },
        {
            "name": "Clinic Appointment Reminder (EN)",
            "subject": "Doctor Appointment Reminder",
            "content": "Reminder: You have a dental checkup scheduled with Dr. Verma tomorrow at 4:30 PM at Apollo Clinic. Please arrive 10 minutes prior to your slot."
        },
        {
            "name": "Credit Card Bill Notice (EN)",
            "subject": "Credit Card Due Date Alert",
            "content": "Dear Cardholder, your credit card statement for ending 8812 is generated. Minimum amount due: Rs 1,200 by 05-Dec-2026. View details in your secure netbanking portal."
        },
        {
            "name": "Telecom Validity Notice (EN)",
            "subject": "Prepaid Plan Expiry Alert",
            "content": "Dear subscriber, your current prepaid unlimited pack validity expires in 3 days on 25-Nov-2026. Recharge with your regular plan to continue uninterrupted services. Telecom Care."
        }
    ]

    print("\n--- Testing 5 Fresh Scam Messages ---")
    scam_results = []
    for m in scam_messages:
        status, res = post_json("/api/analyze/message", {"content": m["content"], "subject": m["subject"]})
        print(f"[{m['name']}] -> Risk: {res['risk_level']} (Score: {res['risk_score']} pts), Category: {res['category']}, Lang: {res['language']}")
        scam_results.append((m['name'], res['risk_level'], res['risk_score'], res['category'], res['indicators']))

    print("\n--- Testing 5 Fresh Genuine Messages ---")
    gen_results = []
    for m in genuine_messages:
        status, res = post_json("/api/analyze/message", {"content": m["content"], "subject": m["subject"]})
        print(f"[{m['name']}] -> Risk: {res['risk_level']} (Score: {res['risk_score']} pts), Category: {res['category']}, Lang: {res['language']}")
        gen_results.append((m['name'], res['risk_level'], res['risk_score'], res['category']))

    print("\n" + "=" * 60)
    print("STEP 3: Test SSRF Block on {'url': 'http://127.0.0.1'} on /api/analyze/website")
    print("=" * 60)
    status_ssrf, res_ssrf = post_json("/api/analyze/website", {"url": "http://127.0.0.1"})
    print(f"Website SSRF Test Result: status={status_ssrf}")
    print(f"  Risk Level: {res_ssrf.get('risk_level')}")
    print(f"  Risk Score: {res_ssrf.get('risk_score')}")
    print(f"  Category: {res_ssrf.get('category')}")
    print(f"  Live Checks info: {res_ssrf.get('live_checks')}")
    print(f"  Indicators: {[i['name'] for i in res_ssrf.get('indicators', [])]}")

    print("\n" + "=" * 60)
    print("STEP 4: Check /api/intelligence/graph for demo-scam.test, phone, and upi")
    print("=" * 60)
    status_g, graph = get_json("/api/intelligence/graph?include_demo=true")
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    print(f"Graph Totals: {len(nodes)} nodes, {len(edges)} edges")
    
    # Check for target nodes
    demo_scam_nodes = [n for n in nodes if "demo-scam.test" in (n.get("value") or "") or "demo-scam.test" in (n.get("label") or "")]
    phone_nodes = [n for n in nodes if "+919000000001" in (n.get("value") or "") or "+919000000001" in (n.get("label") or "")]
    upi_nodes = [n for n in nodes if "demo.pay@demoupi" in (n.get("value") or "") or "demo.pay@demoupi" in (n.get("label") or "")]

    print(f"\nTarget Nodes Found:")
    print(f"  - demo-scam.test node: {demo_scam_nodes}")
    print(f"  - +919000000001 node: {phone_nodes}")
    print(f"  - demo.pay@demoupi node: {upi_nodes}")

    # Check edges connected to these nodes
    target_node_ids = {n["id"] for n in demo_scam_nodes + phone_nodes + upi_nodes}
    connected_edges = [e for e in edges if e["source"] in target_node_ids or e["target"] in target_node_ids]
    print(f"\nEdges connected to target identifiers: {len(connected_edges)} edges")
    for ce in connected_edges[:10]:
        print(f"  Edge: {ce['source']} -> {ce['target']} ({ce.get('label')})")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    run()
