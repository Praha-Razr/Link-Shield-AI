import json
import re
from pathlib import Path
from typing import Dict, Set
from urllib.parse import urlparse

ALLOWLIST_PATH = Path(__file__).resolve().parent / "config" / "legit_identifiers.json"

_ALLOWLIST: Dict[str, Set[str]] = {
    "domains": set(),
    "emails": set(),
    "phones": set()
}

def load_allowlist() -> Dict[str, Set[str]]:
    global _ALLOWLIST
    if ALLOWLIST_PATH.exists():
        try:
            with open(ALLOWLIST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                _ALLOWLIST["domains"] = {d.strip().lower() for d in data.get("domains", [])}
                _ALLOWLIST["emails"] = {e.strip().lower() for e in data.get("emails", [])}
                _ALLOWLIST["phones"] = {p.strip().replace(" ", "") for p in data.get("phones", [])}
        except Exception:
            pass
    return _ALLOWLIST

# Initial load
load_allowlist()

def is_ifsc_code(itype: str, ivalue: str) -> bool:
    """Checks if identifier represents an IFSC branch code."""
    t = (itype or "").strip().lower()
    v = (ivalue or "").strip().upper()
    if t == "ifsc" or v.startswith("IFSC:"):
        return True
    clean_v = v.replace("IFSC", "").replace(":", "").strip()
    if re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", clean_v):
        return True
    return False

def is_legitimate_identifier(itype: str, ivalue: str) -> bool:
    """Checks if identifier is a known legitimate brand/service identifier."""
    if not _ALLOWLIST["domains"]:
        load_allowlist()

    t = (itype or "").strip().lower()
    v = (ivalue or "").strip()

    if t == "domain":
        dom = v.lower()
        if dom in _ALLOWLIST["domains"]:
            return True
        for legit_d in _ALLOWLIST["domains"]:
            if dom.endswith("." + legit_d):
                return True
        return False
    elif t == "url":
        try:
            parsed = urlparse(v if "://" in v else f"http://{v}")
            host = (parsed.hostname or "").lower()
            if host in _ALLOWLIST["domains"]:
                return True
            for legit_d in _ALLOWLIST["domains"]:
                if host.endswith("." + legit_d):
                    return True
        except Exception:
            pass
        return False
    elif t == "email":
        em = v.lower()
        if em in _ALLOWLIST["emails"]:
            return True
        if "@" in em:
            dom_part = em.split("@")[-1]
            if dom_part in _ALLOWLIST["domains"]:
                return True
            for legit_d in _ALLOWLIST["domains"]:
                if dom_part.endswith("." + legit_d):
                    return True
        return False
    elif t == "phone":
        clean_p = v.replace(" ", "")
        return clean_p in _ALLOWLIST["phones"] or clean_p.replace("+91", "") in _ALLOWLIST["phones"]
    return False

def is_linkable_identifier(itype: str, ivalue: str) -> bool:
    """
    Returns True if an identifier is permitted to create graph links,
    heat-list entries, or cross-case linkages.
    IFSC codes and known legitimate identifiers are excluded.
    """
    if is_ifsc_code(itype, ivalue):
        return False
    if is_legitimate_identifier(itype, ivalue):
        return False
    return True
