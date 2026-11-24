"""
Tests for family/friend emergency impersonation scam detection and specificity against genuine money/invoice messages.
"""

import pytest
from app.analyzers.message import analyze_message_content

TARGET_SCAM = (
    "Hi Dad, I lost my phone, this is my new number. Please send Rs 15,000 urgently to my friend's UPI, I'll explain later."
)

M_CASES = [
    (
        "M1",
        "Mom this is my new number, old one is not working. Need Rs 8,000 right now for a hospital bill, send to this account and I will call you tonight.",
        "New number not working hospital bill right now call tonight"
    ),
    (
        "M2",
        "Hello uncle, I'm Rohan's friend. He's in an accident and needs money immediately, please send 20000 on this UPI.",
        "Third-party friend of Rohan accident immediately send UPI"
    ),
    (
        "M3",
        "Hey it's me, got a new SIM. Can you do me a favour and pay my phone bill, I'll send it back tomorrow. Do it fast please.",
        "New SIM favor pay phone bill send back tomorrow fast"
    )
]

L_CASES = [
    (
        "L1",
        "Hi Mom, I got a new phone, this is my new number. Save it. Will call you tonight.",
        "New phone announcement with save number and call tonight, no money"
    ),
    (
        "L2",
        "Dad, I'll reach home by 8. Can you ask Mom to keep dinner ready?",
        "Routine family dinner coordination"
    ),
    (
        "L3",
        "Rent is due, please send 15,000 to my usual account by the 5th. Thanks, landlord.",
        "Routine monthly rent reminder without identity claim or urgency"
    )
]

SCAM_VARIATIONS_EARLIER = [
    (
        "SCAM_TARGET",
        TARGET_SCAM,
        "Original prompt target scam"
    ),
    (
        "SCAM_MUM_WHATSAPP",
        "Hello Mum, my phone is damaged and camera is broken. This is my temporary new number. Can you please pay Rs 25,000 to my college friend's account urgently? Can't talk now in class.",
        "WhatsApp Mum broken phone and college friend account"
    ),
    (
        "SCAM_HINDI_PAPA",
        "नमस्ते पापा, मेरा पुराना फोन खो गया है और यह मेरा नया नंबर है। एक इमरजेंसी आ गई है, कृपया तुरंत मेरे दोस्त के खाते में 20000 रुपये भेज दो। अभी फोन मत करना मैं बाद में बताऊंगा।",
        "Hindi Papa lost phone emergency third-party account"
    ),
    (
        "SCAM_HINGLISH_BHAIYA",
        "Hi bhaiya, mera phone chori ho gaya, save this new number. Ek emergency hai please 10,000 dost ke UPI pe transfer kar do urgently, call mat karna baad me baat karta hu.",
        "Hinglish Bhaiya stolen phone friend UPI"
    ),
    (
        "SCAM_ACCIDENT_SECRECY",
        "Hi Mom, I had a minor car accident and my phone screen shattered, using colleague phone. Urgently need Rs 30,000 to settle repair. Please don't tell anyone, I'll explain later.",
        "Accident secrecy colleague phone lure"
    ),
    (
        "SCAM_HINDI_MOM",
        "माँ मेरा फोन खराब हो गया है यह मेरा नया नंबर है। अस्पताल में दोस्त को तुरंत 15000 रुपये देने हैं, उसकी यूपीआई पर भेज दो, अभी बात नहीं कर सकता।",
        "Hindi Mom broken phone hospital friend UPI"
    )
]

SCAMS_12_NEW = [
    (
        "S_NEW_1",
        "Dad this is my new number, my phone got lost. I am in the emergency room with severe food poisoning, please pay the hospital bill of Rs 6,500 immediately to hospital UPI billdesk.apollo@okaxis. Can't speak right now.",
        "Hospital emergency food poisoning UPI immediately"
    ),
    (
        "S_NEW_2",
        "Hello aunty, I am Priya's college roommate. Priya met with a bike accident and her phone is damaged. Doctor says we need 15000 urgently for scans, please GPay to this number.",
        "Friend roommate bike accident scans urgently"
    ),
    (
        "S_NEW_3",
        "Hey mum it's me! Got a new SIM card today. Can you do a quick favor and recharge my number with 799 or pay my post-paid bill? I'm stuck with zero data and can't call, will return money tomorrow.",
        "WhatsApp new SIM zero data recharge pay bill repay tomorrow"
    ),
    (
        "S_NEW_4",
        "पापा मेरा फोन चोरी हो गया है, यह मेरे दोस्त का नंबर है। ट्रैफिक पुलिस ने मुझे पकड़ लिया है और चालान के लिए तुरंत 5000 रुपये चाहिए, इस यूपीआई पर भेज दो। अभी बात नहीं कर सकता।",
        "Hindi traffic police fine friend number UPI"
    ),
    (
        "S_NEW_5",
        "नमस्ते अंकल, मैं अमित का दोस्त रोहित बोल रहा हूँ। अमित अस्पताल में भर्ती है और उसका फोन बंद है। दवाइयों के लिए 12000 रुपये की तुरंत जरूरत है, कृपया इस खाते में पैसे ट्रांसफर कर दीजिए।",
        "Hindi Amit friend hospital medicines urgent transfer"
    ),
    (
        "S_NEW_6",
        "Hi bro, mera phone kharab ho gaya screen toot gayi, using my office friend phone. Car breakdown ho gaya urgently 8000 mechanic ke UPI pe transfer kar de, I will explain everything tonight.",
        "Hinglish car breakdown screen broken mechanic UPI"
    ),
    (
        "S_NEW_7",
        "Papa ek bahut badi emergency hai, college me issue ho gaya. 25,000 fine turant bharna hai nahi toh rusticate kar denge. Please send on this account immediately, phone mat karna baad me call karunga.",
        "Hinglish college rustication fine emergency send immediately"
    ),
    (
        "S_NEW_8",
        "Hi Dad, my phone and wallet got stolen at the railway station, this is a temporary number from a shopkeeper. Need Rs 3,500 urgently for ticket, please pay on this UPI shopkeeper@upi right now.",
        "Stolen wallet train station shopkeeper UPI ticket"
    ),
    (
        "S_NEW_9",
        "Hello chachi, this is Rahul's office colleague. Rahul fell unconscious at work and we rushed him to clinic. Please transfer Rs 18,000 for deposit on 9876543210 immediately.",
        "Colleague unconscious clinic deposit transfer immediately"
    ),
    (
        "S_NEW_10",
        "भैया मेरा फोन पानी में गिर गया और काम नहीं कर रहा, यह सहेली का नंबर है। एग्जाम फॉर्म की आज आखिरी तारीख है, 4500 रुपये तुरंत इस लिंक/खाते में भेज दो, शाम को फोन करूंगी।",
        "Hindi phone fell in water exam fee send immediately"
    ),
    (
        "S_NEW_11",
        "Mummy mera phone kho gaya hai save this new number. Landlord ghar se nikal raha hai, please 14000 turant is account me daal do, abhi call mat karna network nahi hai.",
        "Hinglish landlord eviction lost phone deposit immediately"
    ),
    (
        "S_NEW_12",
        "Hey it's me Rohit, changed my number. Had a sudden medical emergency with my dog, need 10000 right now, please send to my UPI rohit@icici, will send it back first thing tomorrow morning.",
        "Casual name identity dog medical emergency UPI repay tomorrow"
    )
]

GENUINE_REQUIRED = [
    (
        "GENUINE_INVOICE",
        "Hi, sending the invoice for last month, please pay by Friday. Thanks!",
        "Routine monthly business invoice"
    ),
    (
        "GENUINE_DINNER_SHARE",
        "Please pay your share of the dinner bill: 450 on my UPI when you can",
        "Casual social dinner split"
    ),
    (
        "GENUINE_ELECTRICITY_DUE",
        "Your electricity bill of Rs 1,240 is due 30-Nov; pay via the official app",
        "Standard utility bill reminder"
    ),
    (
        "GENUINE_DEBIT_ALERT",
        "Rs 4,500 debited from A/c XX4102. If not you, call the number on the back of your card",
        "Standard bank debit notification"
    ),
    (
        "GENUINE_BANK_OTP",
        "Your OTP for transaction of Rs 1,000 at Merchant is 482910. Do not share this OTP with anyone.",
        "Standard bank transaction OTP"
    )
]

GENUINE_ADDITIONAL = [
    (
        "GENUINE_FLAT_RENT",
        "Hi bro, rent for this month is 12,000 each. Transfer to my account by 5th.",
        "Roommate monthly rent share"
    ),
    (
        "GENUINE_CAB_SPLIT",
        "Hey, Uber cab was Rs 380, you can GPay me 190 whenever convenient.",
        "Cab fare reimbursement"
    ),
    (
        "GENUINE_FREELANCE_INVOICE",
        "Dear Sir, please find attached the consulting invoice for November. Payment due in 15 days.",
        "Formal consulting services invoice"
    ),
    (
        "GENUINE_BIRTHDAY_GIFT",
        "Guys, collecting 500 each for Rahul's birthday gift. Send on UPI by tomorrow evening!",
        "Group gift contribution"
    ),
    (
        "GENUINE_COLLEGE_PROJECT",
        "Hey, I bought the project components for Rs 850. Please send your half when free.",
        "Shared project expenses split"
    )
]

GENUINE_12_NEW = [
    (
        "G_NEW_1",
        "Hey everyone, finally upgraded to the new iPhone! This is my new number, please save it. Catch up with you guys over the weekend.",
        "New phone announcement with save number, no money request"
    ),
    (
        "G_NEW_2",
        "Hi Dad, our flight just landed at Jaipur airport! Collecting baggage now, can you pick me up from Terminal 2 in about 20 minutes?",
        "Family airport arrival pickup coordination"
    ),
    (
        "G_NEW_3",
        "Mummy, I am leaving office now, will reach home by 8:30 PM. Please don't make rotis for me, I had snacks with colleagues.",
        "Family dinner timing update"
    ),
    (
        "G_NEW_4",
        "Dear tenant, maintenance charge of Rs 2,500 for December is due. Please deposit into the society bank account as usual. Thank you, Secretary.",
        "Routine building society maintenance notice"
    ),
    (
        "G_NEW_5",
        "Hi Team, attached is the invoice for the website design work completed in November. Total amount: Rs 35,000. Payment terms 30 days.",
        "Formal vendor invoice with 30-day terms"
    ),
    (
        "G_NEW_6",
        "Hey guys, movie tickets came to 350 per head. Whenever you get time you can transfer to my UPI, no rush!",
        "Social movie split whenever convenient"
    ),
    (
        "G_NEW_7",
        "Roomie, I picked up groceries and milk for the week, your share is 420. Send it when you are free.",
        "Roommate grocery split when free"
    ),
    (
        "G_NEW_8",
        "Rs 75,000.00 credited to your Salary Account XX1209 on 30-Nov-2024. Available balance: Rs 92,450.00. - HDFC Bank",
        "Official bank salary credit alert"
    ),
    (
        "G_NEW_9",
        "Your Flipkart order containing Running Shoes is out for delivery with our wishmaster. Delivery is contactless. Share OTP only upon receiving package.",
        "E-commerce delivery tracking notice"
    ),
    (
        "G_NEW_10",
        "Your Airtel Unlimited 5G plan of Rs 349 is expiring on 02-Dec-2024. Recharge through the Airtel Thanks app to stay connected.",
        "Official telco plan expiry reminder"
    ),
    (
        "G_NEW_11",
        "पापा, मैं ट्रेन में बैठ गया हूँ। ट्रेन समय पर चल रही है और कल सुबह ७ बजे दिल्ली पहुँचूँगा। आप स्टेशन मत आना, मैं कैब ले लूँगा।",
        "Hindi family train journey update"
    ),
    (
        "G_NEW_12",
        "Dear Patient, your dental checkup with Dr. Verma is confirmed for tomorrow, Tuesday at 5:00 PM at Apollo Clinic. Please arrive 10 minutes early.",
        "Doctor appointment confirmation reminder"
    )
]


def test_target_scam_meets_medium_or_high():
    """Verifies that the target family emergency message scores at least MEDIUM (>= 30)."""
    res = analyze_message_content(TARGET_SCAM)
    assert res["risk_level"] in ("MEDIUM", "HIGH"), f"Target scam scored {res['risk_level']} ({res['risk_score']} pts), expected at least MEDIUM"
    assert res["risk_score"] >= 30, f"Expected score >= 30, got {res['risk_score']}"
    
    # Verify explanation presence
    explanations = [i["explanation"] for i in res["indicators"]]
    expected_expl = "Consistent with a family/friend emergency impersonation scam: verify by calling the person"
    assert any(expected_expl in e for e in explanations), f"Expected combination explanation missing from indicators: {explanations}"


@pytest.mark.parametrize("cid,text,description", M_CASES)
def test_m1_to_m3_detected_as_medium(cid, text, description):
    """Verifies that M1, M2, M3 score at least MEDIUM (score >= 30)."""
    res = analyze_message_content(text)
    assert res["risk_level"] in ("MEDIUM", "HIGH"), (
        f"{cid} [{description}] failed detection: scored {res['risk_level']} ({res['risk_score']} pts). Fired: {[i['name'] for i in res['indicators']]}"
    )
    assert res["risk_score"] >= 30, f"{cid} scored {res['risk_score']}, expected >= 30"
    # Verify it does not escalate to HIGH without link/credential/brand mismatch
    assert res["risk_score"] <= 49, f"{cid} escalated to {res['risk_score']}, expected <= 49 (MEDIUM)"


@pytest.mark.parametrize("cid,text,description", L_CASES)
def test_l1_to_l3_stay_low(cid, text, description):
    """Verifies that L1, L2, L3 strictly stay LOW risk (< 25 pts)."""
    res = analyze_message_content(text)
    assert res["risk_level"] == "LOW", (
        f"{cid} [{description}] FALSE POSITIVE! Scored {res['risk_level']} ({res['risk_score']} pts). Fired: {[i['name'] for i in res['indicators']]}"
    )
    assert res["risk_score"] < 25, f"{cid} score {res['risk_score']} exceeds LOW threshold"


@pytest.mark.parametrize("cid,text,description", SCAM_VARIATIONS_EARLIER + SCAMS_12_NEW)
def test_all_scam_variations_detected(cid, text, description):
    """Verifies that all scam variations score at least MEDIUM (score >= 30)."""
    res = analyze_message_content(text)
    assert res["risk_level"] in ("MEDIUM", "HIGH"), (
        f"{cid} [{description}] failed detection: scored {res['risk_level']} ({res['risk_score']} pts). Fired: {[i['name'] for i in res['indicators']]}"
    )
    assert res["risk_score"] >= 30, f"{cid} scored {res['risk_score']}, expected >= 30"


@pytest.mark.parametrize("cid,text,description", GENUINE_REQUIRED + GENUINE_ADDITIONAL + GENUINE_12_NEW)
def test_all_genuine_messages_stay_low(cid, text, description):
    """Verifies that ordinary genuine messages and invoices strictly remain LOW risk (0-24 pts)."""
    res = analyze_message_content(text)
    assert res["risk_level"] == "LOW", (
        f"{cid} [{description}] FALSE POSITIVE! Scored {res['risk_level']} ({res['risk_score']} pts). "
        f"Fired indicators: {[i['name'] for i in res['indicators']]}"
    )
    assert res["risk_score"] < 25, f"{cid} score {res['risk_score']} exceeds LOW threshold"
