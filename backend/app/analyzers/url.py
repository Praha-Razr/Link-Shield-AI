import urllib.parse
from typing import Dict, Any, List
from app.extractors import extract_all_identifiers
from app.risk.engine import (
    evaluate_risk,
    evaluate_url_structure,
    deduplicate_indicators,
    is_official_domain,
    get_verified_official_info,
    get_safety_recommendations
)
from app.security import safe_fetch_url, validate_url_safety
from app.config import settings
from app.analyzers.rdap import lookup_domain_age, check_google_safe_browsing

def analyze_url_target(
    url_str: str,
    subject: str = None,
    perform_live_check: bool = False
) -> Dict[str, Any]:
    """
    Analyzes a suspicious URL:
    - Static inspections (syntax, structure, brand lookalike, blacklist, HTTPS)
    - Optional safe live check via safe_fetch_url (SSRF protected)
    - Domain age reporting ("Not available")
    """
    clean_url = url_str.strip()
    if not clean_url.lower().startswith(("http://", "https://")):
        clean_url = f"https://{clean_url}"

    parsed = urllib.parse.urlsplit(clean_url)
    domain = (parsed.hostname or "").lower().strip()
    scheme = parsed.scheme.lower()

    # Extract identifiers
    identifiers = extract_all_identifiers(clean_url)

    # Static URL evaluation
    indicators = evaluate_url_structure(clean_url, domain)

    # Insecure scheme check (http without https: +5 per Part 2.2)
    if scheme == "http" and not is_official_domain(domain):
        indicators.append({
            "name": "Unencrypted HTTP Scheme",
            "points": 5,
            "explanation": "URL uses plaintext HTTP instead of secure HTTPS, exposing traffic to interception."
        })

    # Proactive SSRF safety validation (static checks for IP literals/localhost, live DNS only on live check)
    is_safe, ssrf_reason, _ = validate_url_safety(clean_url, resolve_dns=perform_live_check)
    if not is_safe:
        indicators.append({
            "name": "SSRF Prohibited Destination",
            "points": 50,
            "explanation": f"Destination host is blocked by network safety policy: {ssrf_reason}"
        })

    # Real domain age lookup via RDAP (no API key required)
    domain_age_info = lookup_domain_age(domain)

    # Optional Google Safe Browsing Lookup check
    safe_browsing_info = check_google_safe_browsing(clean_url)
    if safe_browsing_info.get("matched"):
        indicators.append({
            "name": "Google Safe Browsing Match",
            "points": 35,
            "explanation": safe_browsing_info.get("reason", "Flagged by Google Safe Browsing as unsafe")
        })

    # Domain age indicators (applicable to public non-allowlisted domains)
    if not is_official_domain(domain):
        age_days = domain_age_info.get("age_days")
        reg_dt = domain_age_info.get("registration_date")
        if age_days is not None:
            if age_days < 30:
                indicators.append({
                    "name": "Newly Registered Domain (<30 days)",
                    "points": 15,
                    "explanation": f"Domain was registered only {age_days} days ago ({reg_dt}). Fraudulent campaigns heavily use newly created domains."
                })
            elif age_days < 90:
                indicators.append({
                    "name": "Recently Registered Domain (<90 days)",
                    "points": 10,
                    "explanation": f"Domain was registered {age_days} days ago ({reg_dt}). Recently registered domains warrant elevated operational scrutiny."
                })

    live_check_info = {
        "performed": perform_live_check,
        "status": "Success" if perform_live_check else "Not performed (static analysis only)",
        "redirect_chain": [],
        "https_available": "Yes" if scheme == "https" else ("Not available (live check not requested)" if not perform_live_check else "No"),
        "resolved_ip": None,
        "domain_age": domain_age_info,
        "safe_browsing": safe_browsing_info,
        "error": None
    }

    if perform_live_check:
        fetch_result = safe_fetch_url(clean_url)
        live_check_info["performed"] = True
        if fetch_result["success"]:
            live_check_info["status"] = "Success"
            live_check_info["redirect_chain"] = fetch_result.get("redirect_chain", [])
            live_check_info["https_available"] = "Yes" if scheme == "https" else "Redirected/Checked"
            live_check_info["resolved_ip"] = fetch_result.get("resolved_ip")
        else:
            live_check_info["status"] = "Blocked or Failed"
            live_check_info["error"] = fetch_result.get("error")
            live_check_info["redirect_chain"] = fetch_result.get("redirect_chain", [])
            live_check_info["resolved_ip"] = fetch_result.get("resolved_ip")
            if fetch_result.get("blocked_by_ssrf"):
                indicators.append({
                    "name": "SSRF Prohibited Destination",
                    "points": 35,
                    "explanation": f"Live fetch blocked: {fetch_result.get('error')}"
                })

    # Run general risk engine with text being the URL itself
    url_risk = evaluate_risk(
        text=clean_url,
        urls=[clean_url],
        domains=[domain]
    )

    # Combine indicators without duplicate names
    combined_indicators = list(url_risk["indicators"])
    for ind in indicators:
        if not any(x["name"] == ind["name"] for x in combined_indicators):
            combined_indicators.append(ind)

    # If the domain is an exact verified official domain, clean false alarms
    if is_official_domain(domain):
        combined_indicators = []
        capped_score = 0
        risk_level = "LOW"
        category = "genuine_service"
    else:
        # Deduplicate overlapping indicators and recompute score capped at 100
        combined_indicators = deduplicate_indicators(combined_indicators)
        raw_score = sum(x["points"] for x in combined_indicators)
        capped_score = max(0, min(settings.RISK_SCORE_CAP, raw_score))

        if capped_score <= settings.RISK_THRESHOLD_LOW_MAX:
            risk_level = "LOW"
        elif capped_score <= settings.RISK_THRESHOLD_MEDIUM_MAX:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        category = "phishing_link" if capped_score >= settings.RISK_THRESHOLD_MEDIUM_MAX else "general_analysis"
        if any("Blacklist" in x["name"] for x in combined_indicators):
            category = "blacklisted_domain"
        elif any("Look-alike" in x["name"] or "Brand Impersonation" in x["name"] for x in combined_indicators):
            category = "brand_impersonation_url"

    verified_official = get_verified_official_info(
        clean_url,
        scheme=scheme,
        risk_score=capped_score,
        indicators=combined_indicators
    )
    recommendations = get_safety_recommendations(risk_level)

    return {
        "subject": subject or f"URL Analysis: {domain or clean_url[:40]}",
        "input_type": "url",
        "raw_content": clean_url,
        "risk_score": capped_score,
        "risk_level": risk_level,
        "category": category,
        "language": "en",
        "indicators": combined_indicators,
        "extracted_identifiers": identifiers,
        "suspicious_phrases": url_risk.get("suspicious_phrases", []),
        "safety_recommendations": recommendations,
        "verified_official": verified_official,
        "domain_age": domain_age_info,
        "live_checks": live_check_info
    }
