import json
import math
import re
import urllib.parse
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from app.config import settings

INDICATORS_JSON_PATH = Path(__file__).resolve().parent / "indicators.json"
BRAND_DOMAINS_PATH = Path(__file__).resolve().parent.parent / "config" / "brand_domains.json"
LEGIT_IDENTIFIERS_PATH = Path(__file__).resolve().parent.parent / "config" / "legit_identifiers.json"

try:
    from rapidfuzz import fuzz
except ImportError:
    class fuzz:
        @staticmethod
        def partial_ratio(s1, s2):
            return 100 if s1 in s2 or s2 in s1 else 0

_INDICATORS_CACHE = None
_BRAND_DOMAINS_CACHE = None
_LEGIT_DOMAINS_CACHE = None

def load_indicator_config() -> dict:
    global _INDICATORS_CACHE
    if _INDICATORS_CACHE is None:
        with open(INDICATORS_JSON_PATH, "r", encoding="utf-8") as f:
            _INDICATORS_CACHE = json.load(f)
    return _INDICATORS_CACHE

def load_brand_domains_config() -> dict:
    global _BRAND_DOMAINS_CACHE
    if _BRAND_DOMAINS_CACHE is None:
        if BRAND_DOMAINS_PATH.exists():
            with open(BRAND_DOMAINS_PATH, "r", encoding="utf-8") as f:
                _BRAND_DOMAINS_CACHE = json.load(f)
        else:
            _BRAND_DOMAINS_CACHE = {}
    return _BRAND_DOMAINS_CACHE

def load_all_official_domains() -> set:
    global _LEGIT_DOMAINS_CACHE
    if _LEGIT_DOMAINS_CACHE is None:
        doms = set()
        # From brand_domains.json
        b_conf = load_brand_domains_config()
        for b_info in b_conf.values():
            for d in b_info.get("official_domains", []):
                doms.add(d.strip().lower())
        # From legit_identifiers.json
        if LEGIT_IDENTIFIERS_PATH.exists():
            try:
                with open(LEGIT_IDENTIFIERS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for d in data.get("domains", []):
                        doms.add(d.strip().lower())
            except Exception:
                pass
        _LEGIT_DOMAINS_CACHE = doms
    return _LEGIT_DOMAINS_CACHE

SUSPICIOUS_TLDS = {
    "xyz", "top", "online", "site", "click", "shop", "icu", "buzz", "live", "vip",
    "info", "cfd", "sbs", "work", "loan", "win", "party", "bid", "pw", "fit", "rest",
    "quest", "monster", "space", "tokyo", "cyou", "fun", "bar", "beauty", "hair",
    "link", "tk", "ml", "ga", "cf", "gq"
}

KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "is.gd", "t.co", "cutt.ly", "shorturl.at", "rb.gy",
    "goo.gl", "ow.ly", "tiny.cc", "bc.vc", "v.gd", "bl.ink", "rebrand.ly", "t.ly",
    "s.id", "clck.ru"
}

FREE_HOSTING_DOMAINS = {
    "weebly.com", "wixsite.com", "blogspot.com", "firebaseapp.com", "web.app",
    "vercel.app", "netlify.app", "github.io", "pages.dev", "glitch.me",
    "000webhostapp.com", "000webhost.com", "site123.me", "mystrikingly.com",
    "render.com", "surge.sh", "ngrok.io", "ngrok-free.app"
}

URL_SUSPICIOUS_KEYWORDS = [
    "login", "verify", "kyc", "update", "secure", "banking", "claim", "reward",
    "bonus", "free", "disbursement", "refund", "aadhaar", "pan", "otp"
]

def get_registered_domain(host: str) -> str:
    """Extracts base registered domain name handling common multi-part TLDs."""
    clean = host.lower().strip()
    if clean.startswith("www."):
        clean = clean[4:]
    parts = clean.split(".")
    if len(parts) <= 2:
        return clean
    two_part_tlds = {"co.in", "gov.in", "org.in", "ac.in", "net.in", "edu.in", "nic.in", "com.au", "co.uk"}
    tld2 = ".".join(parts[-2:])
    if tld2 in two_part_tlds and len(parts) >= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])

def is_official_domain(domain: str) -> bool:
    """Checks whether the domain is an exact verified official domain."""
    clean_domain = domain.lower().strip()
    if clean_domain.startswith("www."):
        clean_domain = clean_domain[4:]
    legit_domains = load_all_official_domains()
    if clean_domain in legit_domains:
        return True
    for legit_d in legit_domains:
        if clean_domain.endswith("." + legit_d):
            return True
    return False

def get_verified_official_info(
    url_or_domain: str,
    scheme: str = "",
    risk_score: int = 0,
    indicators: list = None
) -> Optional[Dict[str, Any]]:
    """
    Checks if a target URL/domain is an exact verified official website:
    - Must use HTTPS (either explicitly in URL scheme or passed as scheme)
    - Zero scam indicators fired
    - Risk score must be LOW (0)
    - Registered domain (or exact host) must be an exact match in brand_domains.json or legit_identifiers.json
    - Substring matches (e.g. sbi-bank.com.fake-domain.top or www.hdfcbank.com.secure-login.cfd) MUST NOT match
    """
    if indicators and len(indicators) > 0:
        return None
    if risk_score > 0:
        return None

    target = (url_or_domain or "").strip()
    if not target:
        return None

    # Determine effective scheme
    eff_scheme = scheme.lower() if scheme else ""
    if target.lower().startswith("https://"):
        eff_scheme = "https"
    elif target.lower().startswith("http://"):
        eff_scheme = "http"

    # HTTPS is required for verified official badge
    if eff_scheme != "https":
        return None

    # Parse host
    parsed = urllib.parse.urlsplit(target if "://" in target else f"https://{target}")
    host = (parsed.hostname or "").lower().strip()
    if not host:
        return None
    if host.startswith("www."):
        clean_host = host[4:]
    else:
        clean_host = host

    reg_domain = get_registered_domain(clean_host)

    # Check brand_domains.json
    brands = load_brand_domains_config()
    for brand_key, b_info in brands.items():
        official_domains = [d.strip().lower() for d in b_info.get("official_domains", [])]
        if reg_domain in official_domains or clean_host in official_domains:
            brand_name = b_info.get("name", brand_key.title())
            return {
                "is_verified": True,
                "brand_name": brand_name,
                "domain": reg_domain,
                "badge_title": f"{brand_name} official website",
                "description": f"This is the official domain of {brand_name}. Enter your credentials only on the official website."
            }

    # Check legit_identifiers.json
    all_legit = load_all_official_domains()
    if reg_domain in all_legit or clean_host in all_legit:
        prefix = reg_domain.split(".")[0]
        brand_name = prefix.upper() if len(prefix) <= 4 else prefix.title()
        return {
            "is_verified": True,
            "brand_name": brand_name,
            "domain": reg_domain,
            "badge_title": f"{brand_name} official website",
            "description": f"This is the official domain of {brand_name}. Enter your credentials only on the official website."
        }

    return None

def get_safety_recommendations(risk_level: str) -> List[str]:
    """Returns risk-level-dependent actionable safety recommendations."""
    recommendations = []
    if risk_level == "HIGH":
        recommendations.append("Do not click links, download attached applications, or provide OTP/credentials.")
        recommendations.append("Do not transfer any money or advance payment to specified accounts or UPI handles.")
        recommendations.append("Report the incident immediately on cybercrime.gov.in or contact helpline 1930.")
    elif risk_level == "MEDIUM":
        recommendations.append("Suspicious: be careful. Do not click links or share details yet.")
        recommendations.append("Verify through the official app/website or by calling a number you already know (such as the one printed on your card).")
        recommendations.append("If unsure, report on cybercrime.gov.in or call 1930.")
    else:  # LOW
        recommendations.append("As a precaution, open links through the official app or website, and never share your OTP, PIN or password.")
        recommendations.append("If this communication asks for money or personal details, confirm with the sender using a number you already know.")
        recommendations.append("Low risk does not guarantee safety. Automated results are not proof.")
    return recommendations

def calculate_shannon_entropy(s: str) -> float:
    """Calculates character entropy to detect high-entropy random hostnames."""
    if not s:
        return 0.0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log(p) / math.log(2.0) for p in prob)

def detect_language(text: str) -> str:
    """Detects language based on character sets and vocabulary."""
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
    if devanagari_chars > 5:
        return "hi"

    hinglish_markers = [
        r'\bkarein\b', r'\bkaro\b', r'\bhai\b', r'\bho\b', r'\bapka\b', r'\baapka\b',
        r'\bkhata\b', r'\bturant\b', r'\bjald\b', r'\bpaise\b', r'\bkamao\b', r'\bbhejo\b',
        r'\bbijli\b', r'\bvibhag\b', r'\bghante\b', r'\bandar\b', r'\broka\b', r'\bjurmana\b'
    ]
    hinglish_hits = sum(1 for p in hinglish_markers if re.search(p, text, re.IGNORECASE))
    if hinglish_hits >= 2:
        return "hinglish"

    return "en"

def evaluate_lookalike_domain(domain: str) -> Tuple[bool, str, int]:
    """
    Checks if a domain looks like a protected brand name (SBI, HDFC, Paytm, etc.).
    Returns (is_lookalike, explanation, points).
    Exact genuine domains are never flagged.
    """
    clean_domain = domain.lower().strip()
    if clean_domain.startswith("www."):
        clean_domain = clean_domain[4:]

    # Exact official domains are verified and safe
    if is_official_domain(clean_domain):
        return False, "", 0

    parts = clean_domain.split(".")
    domain_body = parts[0] if parts else clean_domain

    for brand in settings.TARGET_BRANDS:
        if brand in domain_body:
            return True, f"Domain contains brand name '{brand.upper()}' combined with external elements, consistent with look-alike spoofing.", 40
        ratio = fuzz.partial_ratio(brand, domain_body)
        if ratio >= 85 and len(domain_body) > len(brand):
            return True, f"Domain is visually and phonetically similar to '{brand.upper()}' (edit match), indicating potential typosquatting.", 40

    return False, "", 0

def check_brand_mismatch(text: str, urls: List[str], domains: List[str]) -> List[Dict[str, Any]]:
    """
    Rule 1: If text mentions a brand AND contains a link whose registered domain is NOT
    in that brand's official list, add 'Brand claimed but link goes elsewhere' +25.
    Exact genuine domains must never trigger it.
    """
    brand_configs = load_brand_domains_config()
    indicators = []

    all_target_urls = set(urls)
    for d in domains:
        all_target_urls.add(d if "://" in d else f"http://{d}")

    for brand_key, brand_info in brand_configs.items():
        brand_name = brand_info.get("name", brand_key.upper())
        aliases = brand_info.get("aliases", [brand_key])
        official_domains = {d.lower() for d in brand_info.get("official_domains", [])}

        # Check if text mentions this brand
        brand_claimed = False
        for alias in aliases:
            if re.search(r'[\u0900-\u097F]', alias):
                if alias in text:
                    brand_claimed = True
                    break
            else:
                if re.search(rf'\b{re.escape(alias)}\b', text, re.IGNORECASE):
                    brand_claimed = True
                    break

        if not brand_claimed:
            continue

        # Brand is claimed. Check every URL found in the message
        for u in all_target_urls:
            parsed = urllib.parse.urlsplit(u if "://" in u else f"http://{u}")
            host = (parsed.hostname or "").lower().strip()
            if not host:
                continue
            if host.startswith("www."):
                host = host[4:]

            # Exact genuine domains for this brand never trigger mismatch
            is_genuine_for_brand = any(host == off or host.endswith("." + off) for off in official_domains)
            if is_genuine_for_brand:
                continue

            # Also check if it's an official general gov portal (like cybercrime.gov.in)
            if host in ("cybercrime.gov.in", "police.rajasthan.gov.in", "rajasthan.gov.in"):
                continue

            indicators.append({
                "name": "Brand claimed but link goes elsewhere",
                "points": 25,
                "explanation": (
                    f"Message claims to represent '{brand_name}' but directs recipient to an external or unrelated "
                    f"domain '{host}' rather than the official domain ({', '.join(sorted(list(official_domains))[:2])})."
                )
            })
            break  # One mismatch explanation per brand is sufficient

    return indicators

def evaluate_url_structure(url: str, domain: str) -> List[Dict[str, Any]]:
    """
    Evaluates static URL structure characteristics with general signals:
    - IP address host (+20)
    - URL shorteners (+10)
    - Free hosting/subdomain services (+10)
    - Suspicious TLDs (+10)
    - Brand name inside subdomain or path of unrelated domain (+25)
    - Long random-looking subdomain or high-entropy host (+10)
    - Many hyphens/digits (+10)
    - Links to .apk/.exe/.zip files (+20)
    - '@' or encoded characters in URLs (+10)
    - Unencrypted HTTP scheme (+5)
    Exact official domains are verified and returned clean.
    """
    indicators = []
    clean_url = url.strip()
    clean_domain = domain.lower().strip()
    if clean_domain.startswith("www."):
        clean_domain = clean_domain[4:]

    # Exact verified official domains bypass generic suspicion checks
    if is_official_domain(clean_domain):
        return indicators

    # 1. Check synthetic demo blacklist (exact match or subdomain)
    is_blacklisted = clean_domain in settings.DEMO_BLACKLIST_DOMAINS or any(
        clean_domain.endswith("." + bd) for bd in settings.DEMO_BLACKLIST_DOMAINS
    )
    if is_blacklisted:
        indicators.append({
            "name": "Known Blacklisted Domain",
            "points": 35,
            "explanation": f"Domain '{clean_domain}' matches a known high-risk threat blacklist."
        })

    # 2. Look-alike Brand Check
    is_lookalike, lookalike_expl, lookalike_pts = evaluate_lookalike_domain(clean_domain)
    if is_lookalike:
        indicators.append({
            "name": "Look-alike Brand Domain",
            "points": lookalike_pts,
            "explanation": lookalike_expl
        })

    # 3. IP-address host (+20)
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', clean_domain):
        indicators.append({
            "name": "Numerical IP Address Host",
            "points": 20,
            "explanation": f"Host '{clean_domain}' is a raw numerical IP address instead of a domain name, commonly used to bypass domain reputation checks."
        })

    # 4. URL Shortener (+10)
    if clean_domain in KNOWN_SHORTENERS:
        indicators.append({
            "name": "URL Shortening Service Concealing Destination",
            "points": 10,
            "explanation": f"Domain '{clean_domain}' is a URL shortening service that conceals the true landing page and routing."
        })

    # 5. Free hosting / Cloud Subdomain (+10)
    is_free_host = any(clean_domain == fh or clean_domain.endswith("." + fh) for fh in FREE_HOSTING_DOMAINS)
    if is_free_host:
        indicators.append({
            "name": "Free Public Hosting or Cloud Subdomain",
            "points": 10,
            "explanation": f"Domain '{clean_domain}' is hosted on a free public hosting or cloud platform commonly used to deploy disposable phishing pages."
        })

    # 6. Suspicious TLD (+10)
    tld = clean_domain.split(".")[-1] if "." in clean_domain else ""
    if tld in SUSPICIOUS_TLDS:
        indicators.append({
            "name": "Suspicious or High-Abuse TLD",
            "points": 10,
            "explanation": f"Top-level domain '.{tld}' has a documented high prevalence of low-cost, disposable abusive domain registrations."
        })

    # 7. Brand name inside subdomain or path of an unrelated domain (+25)
    parsed = urllib.parse.urlsplit(clean_url if "://" in clean_url else f"https://{clean_url}")
    path_lower = parsed.path.lower()
    host_parts = clean_domain.split(".")

    brand_configs = load_brand_domains_config()
    for brand_key, brand_info in brand_configs.items():
        aliases = brand_info.get("aliases", [brand_key])
        official_domains = {d.lower() for d in brand_info.get("official_domains", [])}

        # If domain itself is official for this brand, ignore
        if any(clean_domain == off or clean_domain.endswith("." + off) for off in official_domains):
            continue

        for alias in aliases:
            if len(alias) >= 3 and (alias in path_lower or any(alias == part for part in host_parts[:-1])):
                indicators.append({
                    "name": "Brand Impersonation in URL Structure",
                    "points": 25,
                    "explanation": f"URL places recognized brand keyword '{alias.upper()}' inside a subdomain or path of unrelated external host '{clean_domain}'."
                })
                break

    # 8. High-entropy or long randomized subdomain (+10) and Excessive Subdomain Depth (+15)
    if len(host_parts) > 2:
        subdomain = ".".join(host_parts[:-2])
        entropy = calculate_shannon_entropy(subdomain)
        if len(subdomain) > 22 or entropy > 3.6 or re.search(r'[a-f0-9]{10,}', subdomain):
            indicators.append({
                "name": "High-Entropy or Obfuscated Hostname",
                "points": 10,
                "explanation": f"Subdomain '{subdomain}' exhibits high character entropy ({entropy:.2f}) or randomized patterns consistent with DGA or phishing infrastructure."
            })
        if len(host_parts) >= 5:
            indicators.append({
                "name": "Excessive Subdomain Depth",
                "points": 15,
                "explanation": f"Domain exhibits excessive subdomain depth ({len(host_parts) - 2} levels), typical of deceptive multi-tier phishing routing."
            })

    # 9. Excessive hyphens or numeric sequences (+10)
    domain_body = host_parts[0] if host_parts else clean_domain
    digits_count = len(re.findall(r'\d', domain_body))
    hyphens_count = clean_domain.count("-")
    if hyphens_count >= 2 or digits_count >= 3:
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', clean_domain):
            indicators.append({
                "name": "Excessive Hyphens or Numeric Sequences in Domain",
                "points": 10,
                "explanation": f"Domain contains {hyphens_count} hyphens and {digits_count} digits, frequently used to generate disposable look-alike variations."
            })

    # 10. Links to .apk / .exe / .zip files (+20)
    if path_lower.endswith((".apk", ".exe", ".zip", ".bat", ".scr", ".msi")) or ".apk" in path_lower or ".apk" in clean_url.lower():
        indicators.append({
            "name": "Direct Executable or Package Download Link",
            "points": 20,
            "explanation": "URL directly downloads an application package (.apk/.exe/.zip) commonly used for sideloading mobile malware or unauthorized remote control tools."
        })

    # 11. '@' or encoded characters in URL (+10)
    if "@" in clean_url or "%" in clean_url:
        indicators.append({
            "name": "Obfuscated or Exploit URL Syntax",
            "points": 10,
            "explanation": "URL incorporates '@' authentication exploit syntax or percent-encoded characters designed to mislead visual inspection."
        })

    # 12. Phishing sensitive keywords in URL host/path
    matched_kw = [kw for kw in URL_SUSPICIOUS_KEYWORDS if kw in path_lower or any(kw == part for part in host_parts[:-2])]
    if matched_kw and not is_official_domain(clean_domain):
        indicators.append({
            "name": "Suspicious Sensitive Operation Keywords in Host/Path",
            "points": 10,
            "explanation": f"URL incorporates sensitive financial or credential keywords ({', '.join(matched_kw)})."
        })

    return indicators

def deduplicate_indicators(indicators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicates overlapping indicators to avoid double counting identical evidence."""
    has_web_pay = any(i.get("name") == "Suspicious Website Payment Request" for i in indicators)
    has_dir_pay = any(i.get("name") == "Suspicious Direct Payment Request" for i in indicators)

    has_lookalike = any("Look-alike" in i.get("name", "") for i in indicators)
    has_impersonation = any(i.get("name") == "Institutional or Brand Impersonation" for i in indicators)

    seen_names = set()
    deduped = []
    for ind in indicators:
        name = ind.get("name", "")
        if name in seen_names:
            continue
        seen_names.add(name)

        # Consolidate direct payment if website payment request is already present
        if has_web_pay and name == "Suspicious Direct Payment Request":
            continue

        # Consolidate generic impersonation if look-alike brand domain is already present
        if has_lookalike and name == "Institutional or Brand Impersonation":
            continue

        item = dict(ind)
        deduped.append(item)

    return deduped

def evaluate_risk(
    text: str,
    urls: List[str] = None,
    domains: List[str] = None,
    has_payment_request_on_site: bool = False
) -> Dict[str, Any]:
    """
    Core risk evaluation engine.
    - Scans text against indicators with regex / word-boundary matching.
    - Applies brand mismatch rule: mentions brand but links to unrelated domain (+25).
    - Evaluates URL structure signals (shorteners, free hosts, suspicious TLDs, APKs, IP hosts).
    - Applies combination scoring (raising weak signal combos to MEDIUM/HIGH).
    - Protects exact genuine official domains and transactional alerts (keeping them LOW).
    """
    config = load_indicator_config()
    indicator_defs = config.get("indicators", [])
    thresholds = config.get("thresholds", {"low_max": 24, "medium_max": 49, "cap": 100})

    urls = urls or []
    domains = domains or []

    triggered_indicators: List[Dict[str, Any]] = []
    suspicious_phrases: List[str] = []
    has_scam_signals = False

    # 1. Text Indicators check
    for ind in indicator_defs:
        ind_id = ind["id"]
        points = ind["points"]
        name = ind["name"]
        explanation = ind["explanation"]

        all_keywords = []
        all_keywords.extend(ind.get("keywords_en", []))
        all_keywords.extend(ind.get("keywords_hi", []))
        all_keywords.extend(ind.get("keywords_hinglish", []))

        matched_in_indicator = []
        for kw in all_keywords:
            kw_clean = kw.strip()
            if not kw_clean:
                continue
            if re.search(r'[\u0900-\u097F]', kw_clean):
                if kw_clean in text:
                    matched_in_indicator.append(kw_clean)
            else:
                kw_pat = re.sub(r'\\\s+', r'[-_\\s]+', re.escape(kw_clean))
                pattern = rf'\b{kw_pat}\b'
                if re.search(pattern, text, re.IGNORECASE):
                    matched_in_indicator.append(kw_clean)

        if matched_in_indicator:
            # If OTP indicator matched, verify it's not a legitimate safety warning telling user NOT to share
            if ind_id == "otp_credential_theft":
                if re.search(r'\b(do not|never|don\'t|kisi ko na|kisi ke sath.*na)\s+(share|bataye)\b', text, re.IGNORECASE):
                    if not re.search(r'\b(share|send|provide)\s+(the\s+)?(6-digit\s+)?(cancellation\s+)?otp\s+(to|for|sent)\b', text, re.IGNORECASE):
                        continue

            if ind_id == "benign_service_context":
                continue
            else:
                has_scam_signals = True
                triggered_indicators.append({
                    "id": ind_id,
                    "name": name,
                    "points": points,
                    "explanation": explanation
                })
                suspicious_phrases.extend(matched_in_indicator)

    # 2. Brand Mismatch Detection (Rule 1)
    brand_mismatches = check_brand_mismatch(text, urls, domains)
    for bm in brand_mismatches:
        has_scam_signals = True
        triggered_indicators.append(bm)

    # 3. Check URLs and Domains Structure
    for d in domains:
        url_inds = evaluate_url_structure(d, d)
        for u_ind in url_inds:
            has_scam_signals = True
            triggered_indicators.append(u_ind)

    for u in urls:
        parsed = urllib.parse.urlsplit(u if "://" in u else f"https://{u}")
        h = parsed.hostname or ""
        url_inds = evaluate_url_structure(u, h)
        for u_ind in url_inds:
            has_scam_signals = True
            triggered_indicators.append(u_ind)

    # 4. Website payment request check
    if has_payment_request_on_site:
        has_scam_signals = True
        triggered_indicators.append({
            "name": "Suspicious Website Payment Request",
            "points": 15,
            "explanation": "Website directly requests deposits into personal UPI, third-party bank accounts, or cryptocurrency addresses."
        })

    # 5. Benign context reducer:
    # Only applies if NO critical scam signals were found, or suppresses solitary brand mentions
    benign_def = next((x for x in indicator_defs if x["id"] == "benign_service_context"), None)
    if benign_def:
        benign_matches = []
        for kw in benign_def.get("keywords_en", []) + benign_def.get("keywords_hi", []) + benign_def.get("keywords_hinglish", []):
            if kw and (kw in text.lower() or (re.search(r'[\u0900-\u097F]', kw) and kw in text)):
                benign_matches.append(kw)
        if benign_matches:
            # If purely an informational / transactional message without scam URLs or fraud threats
            non_brand_signals = [i for i in triggered_indicators if i.get("name") != "Institutional or Brand Impersonation"]
            if not non_brand_signals:
                triggered_indicators = []  # Clear solitary brand false positives on benign notifications
                has_scam_signals = False
            elif not has_scam_signals:
                triggered_indicators.append({
                    "id": "benign_service_context",
                    "name": benign_def["name"],
                    "points": benign_def["points"],
                    "explanation": benign_def["explanation"]
                })

    # 6. Deduplicate overlapping indicators
    triggered_indicators = deduplicate_indicators(triggered_indicators)

    # 7. Compute initial raw score
    raw_score = sum(item["points"] for item in triggered_indicators)
    capped_score = max(0, min(thresholds.get("cap", 100), raw_score))

    # 8. Combination Scoring Rules (Part 2.4)
    has_any_link = bool(urls or domains)
    has_urgency_threat = any(
        i.get("id") in ("urgency_threat", "electricity_scam", "digital_arrest_extortion", "trai_sim_block", "fastag_toll_scam") or
        "Urgency" in i.get("name", "")
        for i in triggered_indicators
    )
    has_mismatch_or_conceal = any(
        i.get("name") in (
            "Brand claimed but link goes elsewhere",
            "Brand Impersonation in URL Structure",
            "URL Shortening Service Concealing Destination",
            "Free Public Hosting or Cloud Subdomain"
        )
        for i in triggered_indicators
    )
    has_financial_or_kyc = any(
        i.get("id") in (
            "fake_kyc", "fake_loan_offer", "kbc_lottery_prize", "income_tax_gst_refund",
            "investment_guaranteed_return", "ponzi_double_money", "suspicious_payment_instruction",
            "otp_credential_theft", "fake_job_offer"
        ) or "Brand" in i.get("name", "")
        for i in triggered_indicators
    )
    has_otp_or_remote_app = any(
        i.get("id") in ("otp_credential_theft", "remote_access_apk") or
        "OTP" in i.get("name", "") or "Remote Access" in i.get("name", "") or "Executable" in i.get("name", "")
        for i in triggered_indicators
    )

    # Combination 1: Link + Urgency/Threat -> at least MEDIUM (score >= 25)
    if has_any_link and has_urgency_threat:
        if capped_score < 30:
            capped_score = 30
            triggered_indicators.append({
                "name": "Elevated Threat Combination: Link with Urgency Call-to-Action",
                "points": 15,
                "explanation": "Correlation of external action link and urgency/disconnection pressure is characteristic of phishing scams."
            })

    # Combination 2: Brand Mismatch / Shortener / Free Host + Financial / KYC / Prize -> at least HIGH (score >= 50)
    if has_mismatch_or_conceal and has_financial_or_kyc:
        if capped_score < 55:
            capped_score = 55
            triggered_indicators.append({
                "name": "Critical Phishing Combination: Concealed/Mismatch Link with Financial/KYC Lure",
                "points": 25,
                "explanation": "High-risk correlation: communication leverages a trusted brand, KYC, or financial lure while directing user to a disguised or mismatched external link."
            })

    # Combination 3: Request for OTP / PIN / CVV or Remote Access install -> at least MEDIUM (score >= 35)
    if has_otp_or_remote_app:
        if has_urgency_threat or has_any_link or has_financial_or_kyc:
            capped_score = max(capped_score, 55)
        else:
            capped_score = max(capped_score, 35)

    # 4. Family / Friend Emergency Impersonation Detection (Signals A, B, C, D, E)
    # A. Identity / new-contact claim
    p_new_contact = (
        r'\b(this is my new (phone |mobile |sim )?number|got a new (sim|phone|number|mobile)|'
        r'new (sim|phone|number|no\.?|num\b)|save (my |this )?(new )?(number|no\.?)|'
        r'changed my (number|phone)|temporary new (number|no\.?)|using (a |my )?(friend|colleague)\'?s? (phone|number)|'
        r'mera naya (number|no\.?|sim|phone)|naya (number|no\.?|sim|phone) hai|naya number save|'
        r'number change ho gaya|purana phone kho gaya)\b|'
        r'(मेरा नया नंबर|नया नंबर है|नया सिम|नया फोन|नया नंबर सेव)'
    )
    p_broken_contact = (
        r'\b(old (one|number|phone|sim) is not working|not working|lost (my )?phone|'
        r'phone (is )?(broken|damaged|stolen|lost|screen shattered|off)|can\'t reach my old number|'
        r'phone kho gaya|phone toot gaya|phone chori|phone kharab|phone band hai|'
        r'purana number kaam nahi kar raha|chal nahi raha)\b|'
        r'(फोन खो गया|फोन टूट गया|काम नहीं कर रहा|फोन खराब|पुराना नंबर बंद)'
    )
    p_casual_id = (
        r'\b((hey |hi )?it\'?s me|this is [a-zA-Z]+|main hu|mai hu|pehchana|mai bol raha hu)\b'
    )
    p_family_greeting = (
        r'\b(hi|hello|hey|dear)?\s*(mom|mum|mummy|mama|dad|papa|uncle|aunty|auntie|bhaiya|bhai|beta|didi|dada|dadi|nana|nani|chacha|chachi)\b|'
        r'(नमस्ते|प्रणाम)\s*(पापा|माँ|मम्मी|पिताजी|भैया|अंकल|आंटी)|'
        r'(माँ|पापा|मम्मी|पिताजी|चाचा|चाची|भैया|बेटा|अंकल|आंटी)'
    )
    p_third_party_id = (
        r'\b(i(\'m|\s+am)\s+([a-zA-Z]+\'?s?\s+)?(friend|colleague|cousin|brother|sister|roommate)|'
        r'from\s+([a-zA-Z]+\'?s?\s+)?(office|college|team|work|hostel)|'
        r'calling on behalf of|friend of\s+[a-zA-Z]+|[a-zA-Z]+\s+ka\s+(dost|colleague|bhai)|'
        r'[a-zA-Z]+\s+ke\s+(office|college)\s+se)\b|'
        r'(का दोस्त|के ऑफिस से|की तरफ से)'
    )

    has_a1 = bool(re.search(p_new_contact, text, re.I))
    has_a2 = bool(re.search(p_broken_contact, text, re.I))
    has_a3 = bool(re.search(p_casual_id, text, re.I))
    has_a4 = bool(re.search(p_family_greeting, text, re.I))
    has_a5 = bool(re.search(p_third_party_id, text, re.I))

    has_explicit_id_claim = has_a1 or has_a2 or has_a3 or has_a5
    has_A = has_explicit_id_claim or has_a4

    # B. Money request
    p_money_transfer = (
        r'\b(send|transfer|pay|give|gpay|phonepe|paytm|bhej|forward)\s+(rs\.?|inr|rupees|₹)?\s*[\d,]+|'
        r'\b(need|want|urgently need|require)\s+(rs\.?|inr|rupees|₹)?\s*[\d,]+|'
        r'[\d,]+\s*(rs\.?|inr|rupees|₹)?\s*(pe|par|to|ko)?\s*(transfer|send|bhej|de do|pay|gpay|phonepe)|'
        r'\b(send|transfer|pay|give)\s+(some\s+)?money\b|'
        r'\b(paise|rupaye|rupees?|rs\.?)\s*(bhej|transfer|de do|bhejo|chahiye|mang raha)\b|'
        r'\b(paise chahiye|madad chahiye|financial help)\b|'
        r'([\d,]+\s*(रुपये|रुपए|रु|₹).*?(भेज|दे do|देने|ट्रांसफर|डाल)|पैसे\s*.*?(चाहिए|भेज|दे दो|ट्रांसफर|डाल))'
    )
    p_bill_favour = (
        r'\b(pay (my |the )?(phone |mobile |electricity |hospital |medical )?bill|pay my bill|'
        r'recharge my (phone|number|sim)|do me a favo(u)?r and (pay|send)|'
        r'mera bill (bhar|pay)|recharge kar do|bill pay kar do|ek help kar do|favour kar do)\b|'
        r'(बिल भर दो|रिचार्ज कर दो|अस्पताल का बिल)'
    )
    has_B = bool(re.search(p_money_transfer, text, re.I) or re.search(p_bill_favour, text, re.I))

    # C. Time pressure or emotional trigger
    p_time_pressure = (
        r'\b(right now|immediately|urgently|asap|fast|quickly|quick|today only|'
        r'hurry|do it fast|do it quickly|jaldi|turant|abhi|aaj hi|aaj raat tak|fatafat|foran)\b|'
        r'(तुरंत|जल्दी|अभी|आज ही|फटाफट)'
    )
    p_emotional_trigger = (
        r'\b(emergency|accident|hospital|hospital bill|medical bill|doctor|surgery|operation|'
        r'injured|blood|police|arrested|in jail|in trouble|stuck|lost wallet|minor accident|car accident|'
        r'ek emergency hai|accident ho gaya|hospital me hu|aspataal|police pakad|fas gaya hu|musibat me|mushkil me)\b|'
        r'(इमरजेंसी|दुर्घटना|एक्सीडेंट|अस्पताल|मुसीबत में|फंस गया)'
    )
    has_C = bool(re.search(p_time_pressure, text, re.I) or re.search(p_emotional_trigger, text, re.I))

    # D. Payment destination or channel
    p_destination = (
        r'\b(send to |transfer to |pay on |pay to )?(this account|this upi|this number|this gpay|this phonepe|'
        r'friend\'?s? (account|upi|number)|colleague\'?s? (account|upi)|cousin\'?s? (account|upi)|'
        r'hospital account|clinic account|is account (me|pe)|is upi (pe|par)|is number pe|dost ke (account|upi)|dost ko)\b|'
        r'(इस खाते में|इस यूपीआई पर|इस नंबर पर|दोस्त के खाते|दोस्त की यूपीआई)|'
        r'\b[\w.-]+@[\w.-]+\b|'
        r'\b(a/c|account|acct)\s*:?\s*\d{9,18}\b'
    )
    has_D = bool(re.search(p_destination, text, re.I))

    # E. Verification avoidance or delay promise
    p_explicit_avoidance = (
        r'\b(can\'?t talk (now)?|cannot talk (now)?|don\'?t call|do not call|phone is off|'
        r'screen (is )?broken|no network|in class|in meeting|'
        r'i(\'ll|\s*will)\s*explain later|explain later|'
        r'please don\'?t tell anyone|don\'?t tell anyone|keep it secret|'
        r'call mat karna|phone mat karna|baat nahi kar sakta|phone band hai|class me hu|meeting me hu|'
        r'baad me(in)? (bataunga|baat|call)|kisi ko (mat batana|nahi batana))\b|'
        r'(फोन मत करना|अभी बात नहीं कर सकता|फोन बंद है|कॉल मत करना|बाद में बताऊंगा|किसी को मत बताना)'
    )
    p_conditional_delay = (
        r'\b(i(\'ll|\s*will)\s*(call you\s*)?(tonight|later|tomorrow)|will call you (tonight|later)|'
        r'send it back tomorrow|pay you back tomorrow|'
        r'raat ko call karunga|kal wapas (de dunga|bhej dunga))\b|'
        r'(रात को कॉल करूंगा|कल वापस कर दूंगा)'
    )
    has_E = bool(re.search(p_explicit_avoidance, text, re.I) or ((has_B or has_C) and re.search(p_conditional_delay, text, re.I)))

    # Routine context guard
    p_routine_guard = (
        r'\b(rent is due|landlord|usual account|by the \d+(th|st|nd|rd)|invoice for last month|'
        r'when you can|whenever convenient|when free|dinner bill|birthday gift|'
        r'components for rs|consulting invoice|out for delivery|debited from a/c|'
        r'credited to your|your otp is|do not share this otp)\b'
    )
    is_routine = bool(re.search(p_routine_guard, text, re.I))

    # Populate granular indicators
    if has_explicit_id_claim and not any(i.get("id") == "known_person_impersonation" for i in triggered_indicators):
        triggered_indicators.append({
            "id": "known_person_impersonation",
            "name": "Known Person or New Identity Claim",
            "points": 15,
            "explanation": "Claims to be a family member, acquaintance, or someone reaching out from a new SIM, phone, or number."
        })
    elif has_a4 and (has_B or has_C or has_D or has_E) and not any(i.get("id") == "known_person_impersonation" for i in triggered_indicators):
        triggered_indicators.append({
            "id": "known_person_impersonation",
            "name": "Known Person or New Identity Claim",
            "points": 15,
            "explanation": "Claims to be a family member or relative."
        })

    if has_B and not is_routine and not any(i.get("id") == "urgent_money_request" for i in triggered_indicators):
        triggered_indicators.append({
            "id": "urgent_money_request",
            "name": "Request for Funds, Bill Payment, or Financial Transfer",
            "points": 15,
            "explanation": "Requests an urgent money transfer, bill payment, recharge, or financial assistance."
        })

    if has_C and not any(i.get("id") == "time_pressure_or_emergency" for i in triggered_indicators):
        triggered_indicators.append({
            "id": "time_pressure_or_emergency",
            "name": "High Urgency, Emergency, or Crisis Pressure",
            "points": 15,
            "explanation": "Leverages crisis triggers such as accidents, hospital bills, arrests, or extreme urgency to compel action."
        })

    if has_D and not is_routine and not any(i.get("id") == "payment_destination_channel" for i in triggered_indicators):
        triggered_indicators.append({
            "id": "payment_destination_channel",
            "name": "Specific Payment Destination or Channel Specified",
            "points": 10,
            "explanation": "Specifies a particular destination account, UPI handle, or recipient number to receive funds."
        })

    if has_E and (has_A or has_B or has_C) and not any(i.get("id") == "verification_avoidance_or_delay" for i in triggered_indicators):
        triggered_indicators.append({
            "id": "verification_avoidance_or_delay",
            "name": "Communication Barrier or Verification Delay",
            "points": 10,
            "explanation": "Provides excuses to avoid incoming phone calls or promises to call/explain only after funds are sent."
        })

    # Signal 4: Unsolicited request to send money urgently combined with a UPI ID or account number (+10)
    has_urgent_word = bool(re.search(r'\b(urgently|emergency|immediately|turant|jaldi|right now|aaj hi)\b', text, re.I) or re.search(r'(इमरजेंसी|तुरंत|जल्दी)', text))
    has_explicit_upi_or_account = bool(re.search(r'\b[\w.-]+@[\w.-]+\b', text) or re.search(r'\b(a/c|account|acct)\s*:?\s*\d{9,18}\b', text, re.I))

    if has_B and has_urgent_word and has_explicit_upi_or_account and not is_routine:
        if not any(i.get("id") == "unsolicited_urgent_upi_transfer" for i in triggered_indicators):
            triggered_indicators.append({
                "id": "unsolicited_urgent_upi_transfer",
                "name": "Unsolicited Urgent Transfer Request to Account or UPI",
                "points": 10,
                "explanation": "Unsolicited urgent request to send money directly referencing a UPI address or bank account."
            })

    # Combinations (Elevation to at least MEDIUM >= 30):
    is_family_emergency_combo = False
    if has_A and has_B and has_C and has_D:
        is_family_emergency_combo = True
    elif has_A and has_B and not is_routine:
        is_family_emergency_combo = True
    elif has_B and has_C and (has_D or has_E) and not is_routine:
        is_family_emergency_combo = True
    elif has_a5 and has_C and has_B:
        is_family_emergency_combo = True
    elif has_a1 and has_B and (has_C or has_E):
        is_family_emergency_combo = True

    if is_family_emergency_combo:
        capped_score = max(capped_score, 35)
        # Avoid HIGH (cap at 45) unless external link, brand mismatch, or credential theft is present
        has_ext_link = bool(urls or domains or re.search(r'https?://|www\.', text))
        has_cred_theft = any(i.get("id") in ("otp_credential_theft", "remote_access_apk") for i in triggered_indicators)
        has_brand_mism = any("Brand" in i.get("name", "") for i in triggered_indicators)
        if not has_ext_link and not has_cred_theft and not has_brand_mism:
            capped_score = min(capped_score, 45)

        triggered_indicators.append({
            "id": "family_emergency_impersonation_combination",
            "name": "Family or Friend Impersonation Emergency Scam",
            "points": 15,
            "explanation": "Consistent with a family/friend emergency impersonation scam: verify by calling the person on a number you already know."
        })

    # If routine context with no identity claim and no urgency, suppress family indicators
    if is_routine and not has_explicit_id_claim and not has_C:
        triggered_indicators = [
            i for i in triggered_indicators
            if i.get("id") not in (
                "known_person_impersonation", "urgent_money_request", "payment_destination_channel",
                "verification_avoidance_or_delay", "family_emergency_impersonation_combination",
                "unsolicited_urgent_upi_transfer"
            )
        ]

    # Deduplicate again in case combination added extra items
    triggered_indicators = deduplicate_indicators(triggered_indicators)
    capped_score = max(0, min(thresholds.get("cap", 100), capped_score))

    # 9. Determine Risk Level
    if capped_score <= thresholds.get("low_max", 24):
        risk_level = "LOW"
    elif capped_score <= thresholds.get("medium_max", 49):
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    # 10. Category Determination
    category = "general_analysis"
    ind_ids = [item.get("id", "") for item in triggered_indicators]
    ind_names = [item.get("name", "") for item in triggered_indicators]

    if "digital_arrest_extortion" in ind_ids:
        category = "digital_arrest"
    elif "trai_sim_block" in ind_ids:
        category = "telecom_fraud"
    elif "kbc_lottery_prize" in ind_ids:
        category = "lottery_fraud"
    elif "income_tax_gst_refund" in ind_ids:
        category = "tax_refund_fraud"
    elif "fastag_toll_scam" in ind_ids:
        category = "fastag_fraud"
    elif "otp_credential_theft" in ind_ids:
        category = "credential_phishing"
    elif "remote_access_apk" in ind_ids:
        category = "malware_apk_fraud"
    elif "fake_kyc" in ind_ids:
        category = "fake_kyc"
    elif "electricity_scam" in ind_ids:
        category = "electricity_scam"
    elif "parcel_delivery_scam" in ind_ids:
        category = "parcel_scam"
    elif "fake_job_offer" in ind_ids:
        category = "job_fraud"
    elif "investment_guaranteed_return" in ind_ids or "ponzi_double_money" in ind_ids:
        category = "investment_fraud"
    elif "mlm_referral_chain" in ind_ids:
        category = "mlm_fraud"
    elif "illegal_betting" in ind_ids:
        category = "illegal_betting"
    elif "fake_loan_offer" in ind_ids:
        category = "loan_fraud"
    elif any(i in ind_ids for i in ("family_emergency_impersonation_combination", "known_person_impersonation")) or any("Family or Friend" in name for name in ind_names):
        category = "impersonation_fraud"
    elif any("Look-alike" in name or "Blacklisted" in name or "Brand Impersonation" in name for name in ind_names):
        category = "phishing_link"
    elif risk_level == "LOW":
        category = "genuine_service"

    # 11. Actionable Recommendations by risk level
    recommendations = get_safety_recommendations(risk_level)

    language = detect_language(text)

    return {
        "risk_score": capped_score,
        "risk_level": risk_level,
        "category": category,
        "language": language,
        "indicators": triggered_indicators,
        "suspicious_phrases": sorted(list(set(suspicious_phrases))),
        "safety_recommendations": recommendations
    }
