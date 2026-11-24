import re
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger("linkshield.rdap")

# In-memory cache for RDAP queries to avoid redundant network traffic
RDAP_CACHE: Dict[str, Dict[str, Any]] = {}

def lookup_domain_age(domain: str) -> Dict[str, Any]:
    """
    Queries RDAP (https://rdap.org/domain/<domain>) with 5s timeout.
    Returns age in days, registration date, or safe 'Not available' reason.
    """
    d = domain.lower().strip()
    if d.startswith("www."):
        d = d[4:]

    # Check reserved or test domains
    if any(d.endswith(suffix) for suffix in (".test", ".example", ".invalid", ".localhost")) or d in ("localhost", "127.0.0.1"):
        return {
            "status": "Not available",
            "reason": "Reserved or synthetic test domain (.test, .example, localhost)",
            "age_days": None,
            "registration_date": None,
            "formatted": "Not available (reserved test domain)"
        }

    # Direct IP addresses
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', d):
        return {
            "status": "Not available",
            "reason": "Direct IP address target (no WHOIS/RDAP domain registration)",
            "age_days": None,
            "registration_date": None,
            "formatted": "Not available (IP address)"
        }

    if d in RDAP_CACHE:
        return RDAP_CACHE[d]

    url = f"https://rdap.org/domain/{d}"
    try:
        with httpx.Client(timeout=5.0, follow_redirects=True) as client:
            resp = client.get(url, headers={"Accept": "application/rdap+json, application/json"})
            if resp.status_code == 200:
                data = resp.json()
                events = data.get("events", [])
                reg_date_str = None
                for ev in events:
                    if ev.get("eventAction") in ("registration", "created", "creation"):
                        reg_date_str = ev.get("eventDate")
                        break

                if reg_date_str:
                    clean_iso = reg_date_str.replace("Z", "+00:00")
                    dt = datetime.fromisoformat(clean_iso)
                    now = datetime.now(timezone.utc)
                    age_days = (now - dt).days
                    res = {
                        "status": "Available",
                        "age_days": age_days,
                        "registration_date": reg_date_str[:10],
                        "formatted": f"{age_days} days (Registered {reg_date_str[:10]})",
                        "reason": None
                    }
                    RDAP_CACHE[d] = res
                    return res
                else:
                    res = {
                        "status": "Not available",
                        "reason": "Registration date not recorded in RDAP events",
                        "age_days": None,
                        "registration_date": None,
                        "formatted": "Not available (no registration event)"
                    }
                    RDAP_CACHE[d] = res
                    return res
            elif resp.status_code == 404:
                res = {
                    "status": "Not available",
                    "reason": "Domain not registered in public TLD registry (NXDOMAIN)",
                    "age_days": None,
                    "registration_date": None,
                    "formatted": "Not available (unregistered domain)"
                }
                RDAP_CACHE[d] = res
                return res
            else:
                return {
                    "status": "Not available",
                    "reason": f"RDAP query returned HTTP {resp.status_code}",
                    "age_days": None,
                    "registration_date": None,
                    "formatted": f"Not available (status {resp.status_code})"
                }
    except httpx.TimeoutException:
        logger.info(f"RDAP lookup for '{d}' timed out (5s limit)")
        return {
            "status": "Not available",
            "reason": "RDAP query timed out (5s limit)",
            "age_days": None,
            "registration_date": None,
            "formatted": "Not available (timed out)"
        }
    except Exception as e:
        logger.info(f"RDAP lookup for '{d}' failed: {e}")
        return {
            "status": "Not available",
            "reason": f"RDAP connection error: {type(e).__name__}",
            "age_days": None,
            "registration_date": None,
            "formatted": "Not available (lookup failed)"
        }

def check_google_safe_browsing(target_url: str) -> Dict[str, Any]:
    """
    Checks URL against Google Safe Browsing Lookup API if GOOGLE_SAFE_BROWSING_KEY is set.
    """
    api_key = getattr(settings, "GOOGLE_SAFE_BROWSING_KEY", "")
    if not api_key:
        return {
            "status": "Not available (not configured)",
            "reason": "GOOGLE_SAFE_BROWSING_KEY is not set in environment",
            "matched": False
        }

    url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    payload = {
        "client": {"clientId": "linkshield-ai", "clientVersion": "1.0.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": target_url}]
        }
    }
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                matches = data.get("matches", [])
                if matches:
                    threat_types = [m.get("threatType") for m in matches]
                    return {
                        "status": "FLAGGED",
                        "matched": True,
                        "threat_types": threat_types,
                        "reason": f"Flagged in Google Safe Browsing: {', '.join(threat_types)}"
                    }
                else:
                    return {
                        "status": "Clean",
                        "matched": False,
                        "reason": "No threat matches found in Google Safe Browsing lists"
                    }
            else:
                return {
                    "status": "Error",
                    "matched": False,
                    "reason": f"Safe Browsing API returned status {resp.status_code}"
                }
    except Exception as e:
        return {
            "status": "Error",
            "matched": False,
            "reason": f"Safe Browsing lookup failed: {type(e).__name__}"
        }
