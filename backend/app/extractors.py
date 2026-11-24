import re
import urllib.parse
from typing import Dict, List, Set, Any

EMAIL_REGEX = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')
# UPI ID: username@handle where handle contains NO DOT, or matches known banking handles
UPI_REGEX = re.compile(r'\b[a-zA-Z0-9.\-_]{2,49}@[a-zA-Z0-9]{2,30}\b')

# Indian phone number: optional +91 / 91 / 0 followed by 10 digits starting with 6-9
PHONE_REGEX = re.compile(r'(?:(?:\+91|91|0)[\s\-]*)?([6-9]\d{2,4}[\s\-]*\d{2,4}[\s\-]*\d{2,4})\b')

# Full or partial URLs
URL_REGEX = re.compile(r'(?:https?://[^\s<>"]+|www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s<>"]*)?)', re.IGNORECASE)

# Bank account indicators context words
BANK_CONTEXT_WORDS = [
    r'account', r'acc\b', r'a/c', r'a\s*/\s*c', r'acct', r'khata', r'खाता',
    r'bank\s*a/c', r'acc\s*no', r'a/c\s*no', r'account\s*no', r'ifsc'
]
BANK_CONTEXT_PATTERN = re.compile('|'.join(BANK_CONTEXT_WORDS), re.IGNORECASE)
IFSC_REGEX = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', re.IGNORECASE)

# Crypto wallet patterns
BTC_LEGACY_REGEX = re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b')
BTC_BECH32_REGEX = re.compile(r'\bbc1[a-z0-9]{38,59}\b', re.IGNORECASE)
ETH_REGEX = re.compile(r'\b0x[a-fA-F0-9]{40}\b')
TRON_REGEX = re.compile(r'\bT[1-9A-HJ-NP-Za-km-z]{33}\b')

def extract_emails(text: str) -> List[str]:
    matches = EMAIL_REGEX.findall(text)
    cleaned = []
    for m in matches:
        val = m.strip().lower().rstrip(".,;!?:")
        if val and "@" in val and "." in val.split("@")[-1]:
            cleaned.append(val)
    return sorted(list(set(cleaned)))

def extract_upi_ids(text: str) -> List[str]:
    raw_matches = UPI_REGEX.findall(text)
    emails = set(extract_emails(text))
    results = set()
    for m in raw_matches:
        val = m.strip().lower().rstrip(".,;!?:")
        # Ensure it does NOT have a dot in the handle (domain) part, which distinguishes UPI from email
        parts = val.split("@")
        if len(parts) == 2:
            handle = parts[1]
            if "." not in handle and val not in emails and len(parts[0]) >= 2:
                results.add(val)
    return sorted(list(results))

def extract_phone_numbers(text: str) -> List[str]:
    results = set()
    for match in PHONE_REGEX.finditer(text):
        raw = match.group(0)
        digits = re.sub(r'\D', '', raw)
        # Handle +91, 91 or 0 prefix
        if len(digits) == 12 and digits.startswith("91") and digits[2] in "6789":
            norm = f"+91{digits[2:]}"
            results.add(norm)
        elif len(digits) == 11 and digits.startswith("0") and digits[1] in "6789":
            norm = f"+91{digits[1:]}"
            results.add(norm)
        elif len(digits) == 10 and digits[0] in "6789":
            norm = f"+91{digits}"
            results.add(norm)
    return sorted(list(results))

def extract_urls_and_domains(text: str) -> Dict[str, List[str]]:
    raw_urls = URL_REGEX.findall(text)
    urls = set()
    domains = set()

    for u in raw_urls:
        clean = u.strip().rstrip(".,;!?:)>\"'")
        if not clean:
            continue
        if not clean.lower().startswith(("http://", "https://")):
            url_with_scheme = f"https://{clean}"
        else:
            url_with_scheme = clean

        try:
            parsed = urllib.parse.urlsplit(url_with_scheme)
            hostname = parsed.hostname
            if hostname:
                domain_norm = hostname.lower().strip()
                domains.add(domain_norm)
                # Normalized URL: lowercase scheme & host, preserve path
                norm_url = urllib.parse.urlunsplit((
                    parsed.scheme.lower(),
                    domain_norm + (f":{parsed.port}" if parsed.port else ""),
                    parsed.path or "/",
                    parsed.query,
                    ""
                ))
                urls.add(norm_url)
        except Exception:
            continue

    return {
        "urls": sorted(list(urls)),
        "domains": sorted(list(domains))
    }

def extract_bank_accounts_and_ifsc(text: str) -> Dict[str, List[str]]:
    accounts = set()
    ifsc_codes = set()

    # Find IFSC codes
    for m in IFSC_REGEX.finditer(text):
        code = m.group(0).upper().strip()
        ifsc_codes.add(code)

    # Find bank account numbers (9-18 digits) near bank keywords
    # Scan text with a sliding context window
    lines = text.splitlines()
    for line in lines:
        if BANK_CONTEXT_PATTERN.search(line):
            digit_seqs = re.findall(r'\b\d{9,18}\b', line)
            for num in digit_seqs:
                # Discard if it looks like a phone number (+919...) or timestamp
                if len(num) == 10 and num[0] in "6789":
                    # Could be phone, check context strictly
                    if re.search(r'(?:account|a/c|khata|खाता)\s*[:#\-\s]*' + num, line, re.IGNORECASE):
                        accounts.add(num)
                else:
                    accounts.add(num)

    # Also scan text globally around bank keywords within 50 chars
    for match in BANK_CONTEXT_PATTERN.finditer(text):
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        window = text[start:end]
        for num in re.findall(r'\b\d{9,18}\b', window):
            if not (len(num) == 10 and num[0] in "6789"):
                accounts.add(num)

    return {
        "bank_accounts": sorted(list(accounts)),
        "ifsc_codes": sorted(list(ifsc_codes))
    }

def extract_crypto_wallets(text: str) -> List[Dict[str, str]]:
    wallets = []
    seen = set()

    # BTC Bech32 (preserve case)
    for m in BTC_BECH32_REGEX.findall(text):
        val = m.strip()
        if val not in seen:
            seen.add(val)
            wallets.append({"type": "crypto_wallet", "subtype": "BTC_bech32", "value": val})

    # BTC Legacy (strictly case-sensitive, do not lowercase)
    for m in BTC_LEGACY_REGEX.findall(text):
        val = m.strip()
        if val not in seen and len(val) >= 26:
            seen.add(val)
            wallets.append({"type": "crypto_wallet", "subtype": "BTC_legacy", "value": val})

    # ETH (0x + 40 hex: preserve original casing for display)
    for m in ETH_REGEX.findall(text):
        val = m.strip()
        if val not in seen:
            seen.add(val)
            wallets.append({"type": "crypto_wallet", "subtype": "ETH", "value": val})

    # TRON
    for m in TRON_REGEX.findall(text):
        val = m.strip()
        if val not in seen and len(val) == 34:
            seen.add(val)
            wallets.append({"type": "crypto_wallet", "subtype": "TRON", "value": val})

    return wallets

def extract_all_identifiers(text: str) -> List[Dict[str, str]]:
    """
    Extracts all supported identifiers and returns list of dicts:
    [{"type": "domain"|"url"|"phone"|"upi"|"email"|"bank_account"|"crypto_wallet", "value": "..."}]
    """
    results: List[Dict[str, str]] = []
    seen = set()

    def add_item(t: str, v: str):
        key = (t, v)
        if key not in seen:
            seen.add(key)
            results.append({"type": t, "value": v})

    # URLs and Domains
    url_data = extract_urls_and_domains(text)
    for d in url_data["domains"]:
        add_item("domain", d)
    for u in url_data["urls"]:
        add_item("url", u)

    # Emails
    for e in extract_emails(text):
        add_item("email", e)

    # UPI IDs
    for upi in extract_upi_ids(text):
        add_item("upi", upi)

    # Phones
    for p in extract_phone_numbers(text):
        add_item("phone", p)

    # Bank accounts and IFSC
    bank_data = extract_bank_accounts_and_ifsc(text)
    for a in bank_data["bank_accounts"]:
        add_item("bank_account", a)
    for ifsc in bank_data["ifsc_codes"]:
        add_item("bank_account", f"IFSC:{ifsc}")

    # Crypto
    for c in extract_crypto_wallets(text):
        add_item("crypto_wallet", c["value"])

    return results
