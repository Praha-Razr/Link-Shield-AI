import urllib.parse
from typing import Dict, Any, List
from app.extractors import extract_all_identifiers, extract_urls_and_domains
from app.risk.engine import evaluate_risk, deduplicate_indicators, get_safety_recommendations
from app.analyzers.url import analyze_url_target
from app.config import settings

def analyze_message_content(content: str, subject: str = None) -> Dict[str, Any]:
    """
    Analyzes a suspicious text message (SMS, WhatsApp, Email text):
    - Extracts all identifiers (phones, UPIs, emails, bank accounts, crypto, URLs, domains)
    - Statically analyzes each URL found using URL analyzer
    - Runs multilingual text indicators (EN, HI, Hinglish)
    - Computes explainable risk score and category
    """
    clean_text = content.strip()
    
    # 1. Extract all identifiers
    identifiers = extract_all_identifiers(clean_text)
    
    # 2. Extract URLs and domains
    url_domain_data = extract_urls_and_domains(clean_text)
    urls = url_domain_data["urls"]
    domains = url_domain_data["domains"]
    
    # 3. Evaluate message text risk
    risk_data = evaluate_risk(
        text=clean_text,
        urls=urls,
        domains=domains
    )
    
    indicators = list(risk_data["indicators"])
    
    # 4. Statically analyze each URL found (no network request)
    verified_links = []
    for u in urls:
        url_analysis = analyze_url_target(u, perform_live_check=False)
        for u_ind in url_analysis.get("indicators", []):
            if not any(x["name"] == u_ind["name"] for x in indicators):
                indicators.append(u_ind)

        parsed_u = urllib.parse.urlsplit(u if "://" in u else f"https://{u}")
        u_domain = (parsed_u.hostname or "").lower()
        if u_domain.startswith("www."):
            u_domain = u_domain[4:]

        v_info = url_analysis.get("verified_official")
        if v_info and v_info.get("is_verified"):
            verified_links.append({
                "url": u,
                "domain": u_domain,
                "is_official": True,
                "brand_name": v_info.get("brand_name"),
                "status": "official website",
                "label": f"Link to {u_domain}: official website"
            })
        elif url_analysis.get("risk_level") == "LOW" and len(url_analysis.get("indicators", [])) == 0:
            verified_links.append({
                "url": u,
                "domain": u_domain,
                "is_official": False,
                "brand_name": None,
                "status": "no scam signs found",
                "label": f"Link to {u_domain}: no scam signs found"
            })
        else:
            verified_links.append({
                "url": u,
                "domain": u_domain,
                "is_official": False,
                "brand_name": None,
                "status": "suspicious link",
                "label": f"Link to {u_domain}: suspicious link ({url_analysis.get('risk_level')})"
            })
    
    # 5. Deduplicate overlapping signals and recompute score capped at 100
    indicators = deduplicate_indicators(indicators)
    if urls:
        raw_score = sum(x["points"] for x in indicators)
        capped_score = max(0, min(settings.RISK_SCORE_CAP, raw_score))
    else:
        capped_score = risk_data["risk_score"]
    
    if capped_score <= settings.RISK_THRESHOLD_LOW_MAX:
        risk_level = "LOW"
    elif capped_score <= settings.RISK_THRESHOLD_MEDIUM_MAX:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
        
    category = risk_data["category"]
    # If URLs drove the risk higher
    if category == "genuine_service" and risk_level != "LOW":
        category = "suspicious_message"
        
    # Generate default subject if not provided
    if not subject:
        words = clean_text.split()
        first_few = " ".join(words[:6])
        subject = f"{first_few}..." if len(words) > 6 else first_few
        
    recommendations = get_safety_recommendations(risk_level)

    return {
        "subject": subject,
        "input_type": "message",
        "raw_content": clean_text,
        "risk_score": capped_score,
        "risk_level": risk_level,
        "category": category,
        "language": risk_data["language"],
        "indicators": indicators,
        "extracted_identifiers": identifiers,
        "suspicious_phrases": risk_data.get("suspicious_phrases", []),
        "safety_recommendations": recommendations,
        "verified_links": verified_links
    }
