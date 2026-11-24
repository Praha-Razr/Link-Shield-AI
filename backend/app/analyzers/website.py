import re
import urllib.parse
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from app.extractors import (
    extract_all_identifiers,
    extract_emails,
    extract_phone_numbers,
    extract_upi_ids,
    extract_bank_accounts_and_ifsc,
    extract_crypto_wallets
)
from app.risk.engine import (
    evaluate_risk,
    evaluate_url_structure,
    deduplicate_indicators,
    get_verified_official_info,
    get_safety_recommendations
)
from app.security import safe_fetch_url
from app.config import settings
from app.analyzers.rdap import lookup_domain_age, check_google_safe_browsing

PAYMENT_PROMPT_KEYWORDS = [
    r'deposit\s*(?:here|amount|funds|money|to)',
    r'pay\s*(?:via|through|to)\s*upi',
    r'send\s*(?:payment|funds|money)\s*to',
    r'transfer\s*(?:money|funds|to\s*account)',
    r'wallet\s*address\s*[:#]',
    r'upi\s*id\s*[:#]',
    r'bank\s*details\s*for\s*deposit',
    r'scan\s*qr\s*to\s*pay',
    r'crypto\s*deposit'
]
PAYMENT_PROMPT_REGEX = re.compile('|'.join(PAYMENT_PROMPT_KEYWORDS), re.IGNORECASE)

def analyze_website_content(
    url: Optional[str] = None,
    html_content: Optional[str] = None,
    subject: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyzes website source (either from safe fetch of URL or uploaded HTML):
    - Strips scripts and executable tags (static analysis only)
    - Extracts visible text, links, tel:, mailto: attributes
    - Extracts all identifiers from visible text and attributes
    - Checks for fraudulent patterns and payment request instructions
    """
    fetch_meta = {"fetched": False, "status": "Not fetched", "resolved_ip": None}
    raw_html = ""

    if url and not html_content:
        fetch_result = safe_fetch_url(url)
        fetch_meta["fetched"] = True
        if not fetch_result["success"]:
            # If safe fetch fails or is blocked by SSRF
            return {
                "subject": subject or f"Website: {url[:50]}",
                "input_type": "website",
                "raw_content": f"URL: {url}\nFetch Error: {fetch_result.get('error')}",
                "risk_score": 75 if fetch_result.get("blocked_by_ssrf") else 35,
                "risk_level": "HIGH" if fetch_result.get("blocked_by_ssrf") else "MEDIUM",
                "category": "blocked_destination" if fetch_result.get("blocked_by_ssrf") else "unreachable_website",
                "language": "en",
                "indicators": [
                    {
                        "name": "SSRF or Fetch Failure",
                        "points": 75 if fetch_result.get("blocked_by_ssrf") else 35,
                        "explanation": f"Website analysis could not proceed: {fetch_result.get('error')}"
                    }
                ],
                "extracted_identifiers": [],
                "suspicious_phrases": [],
                "safety_recommendations": ["Do not attempt to navigate to unreachable or restricted network destinations."],
                "live_checks": fetch_result
            }
        raw_html = fetch_result["content"]
        fetch_meta["status"] = "Success"
        fetch_meta["resolved_ip"] = fetch_result.get("resolved_ip")
        fetch_meta["redirect_chain"] = fetch_result.get("redirect_chain", [])
    elif html_content:
        raw_html = html_content
    else:
        raise ValueError("Either 'url' or 'html_content' must be provided.")

    if url:
        parsed_web_u = urllib.parse.urlsplit(url if "://" in url else f"https://{url}")
        target_web_d = (parsed_web_u.hostname or "").lower()
        fetch_meta["domain_age"] = lookup_domain_age(target_web_d)
        fetch_meta["safe_browsing"] = check_google_safe_browsing(url)
    else:
        fetch_meta["domain_age"] = {
            "status": "Not available",
            "reason": "Direct HTML upload (no domain target specified)",
            "age_days": None,
            "registration_date": None,
            "formatted": "Not available (direct HTML upload)"
        }
        fetch_meta["safe_browsing"] = {
            "status": "Not available (not configured)",
            "reason": "Direct HTML upload (no URL target)",
            "matched": False
        }

    # 1. Parse HTML with BeautifulSoup (NEVER execute scripts)
    soup = BeautifulSoup(raw_html, "html.parser")

    # Extract page title
    page_title = ""
    if soup.title and soup.title.string:
        page_title = soup.title.string.strip()

    # 2. Extract attribute identifiers before stripping tags
    tel_numbers = []
    mailto_emails = []
    href_links = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("tel:"):
            tel_numbers.append(href[4:])
        elif href.lower().startswith("mailto:"):
            mailto_emails.append(href[7:].split("?")[0])
        elif href.lower().startswith(("http://", "https://")):
            href_links.append(href)

    # 3. Strip all scripts, styles, objects, iframes, embeds
    for script_tag in soup(["script", "style", "noscript", "iframe", "object", "embed", "svg"]):
        script_tag.extract()

    # Extract clean visible text
    visible_text = soup.get_text(separator=" ", strip=True)

    # 4. Extract identifiers from visible text and attributes
    all_identifiers = []
    seen_ids = set()

    def add_id(t: str, v: str):
        key = (t, v)
        if key not in seen_ids:
            seen_ids.add(key)
            all_identifiers.append({"type": t, "value": v})

    # From visible text
    for item in extract_all_identifiers(visible_text):
        add_id(item["type"], item["value"])

    # From attributes
    for t in tel_numbers:
        for p in extract_phone_numbers(t):
            add_id("phone", p)

    for m in mailto_emails:
        for e in extract_emails(m):
            add_id("email", e)

    # Domains from href links
    domain_list = []
    if url:
        parsed_url = urllib.parse.urlsplit(url)
        if parsed_url.hostname:
            add_id("domain", parsed_url.hostname.lower())
            domain_list.append(parsed_url.hostname.lower())

    for link in href_links[:30]:
        add_id("url", link)
        try:
            h = urllib.parse.urlsplit(link).hostname
            if h:
                add_id("domain", h.lower())
                domain_list.append(h.lower())
        except Exception:
            pass

    # 5. Check payment request keyword presence on page
    has_payment_request = bool(PAYMENT_PROMPT_REGEX.search(visible_text))
    # Also check if crypto wallet or UPI is present along with deposit/pay text
    has_crypto_or_upi = any(x["type"] in ("crypto_wallet", "upi") for x in all_identifiers)
    if has_crypto_or_upi and any(w in visible_text.lower() for w in ["deposit", "recharge", "transfer", "pay", "invest"]):
        has_payment_request = True

    # 6. Evaluate risk
    risk_data = evaluate_risk(
        text=visible_text,
        urls=[url] if url else [],
        domains=domain_list,
        has_payment_request_on_site=has_payment_request
    )

    indicators = list(risk_data["indicators"])

    # If URL provided, also check static URL indicators
    if url:
        parsed = urllib.parse.urlsplit(url)
        url_indicators = evaluate_url_structure(url, parsed.hostname or "")
        for u_ind in url_indicators:
            if not any(x["name"] == u_ind["name"] for x in indicators):
                indicators.append(u_ind)

    # Deduplicate overlapping indicators and recompute score
    indicators = deduplicate_indicators(indicators)
    raw_score = sum(x["points"] for x in indicators)
    capped_score = max(0, min(settings.RISK_SCORE_CAP, raw_score))

    if capped_score <= settings.RISK_THRESHOLD_LOW_MAX:
        risk_level = "LOW"
    elif capped_score <= settings.RISK_THRESHOLD_MEDIUM_MAX:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    category = risk_data["category"]
    if category == "genuine_service" and risk_level != "LOW":
        category = "fraudulent_website"

    case_subject = subject
    if not case_subject:
        if page_title:
            case_subject = f"Website: {page_title[:60]}"
        elif url:
            case_subject = f"Website: {url[:50]}"
        else:
            first_words = " ".join(visible_text.split()[:6])
            case_subject = f"Website Analysis: {first_words}..."

    # Truncate raw content for database evidence (first 10000 chars of HTML or text)
    evidence_content = raw_html[:15000] if len(raw_html) > 15000 else raw_html

    verified_official = None
    if url:
        parsed_url = urllib.parse.urlsplit(url)
        verified_official = get_verified_official_info(
            url,
            scheme=parsed_url.scheme,
            risk_score=capped_score,
            indicators=indicators
        )

    recommendations = get_safety_recommendations(risk_level)

    return {
        "subject": case_subject,
        "input_type": "website",
        "raw_content": evidence_content,
        "risk_score": capped_score,
        "risk_level": risk_level,
        "category": category,
        "language": risk_data["language"],
        "indicators": indicators,
        "extracted_identifiers": all_identifiers,
        "suspicious_phrases": risk_data.get("suspicious_phrases", []),
        "safety_recommendations": recommendations,
        "verified_official": verified_official,
        "live_checks": fetch_meta
    }
