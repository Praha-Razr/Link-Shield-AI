from app.extractors import (
    extract_emails,
    extract_upi_ids,
    extract_phone_numbers,
    extract_urls_and_domains,
    extract_bank_accounts_and_ifsc,
    extract_crypto_wallets,
    extract_all_identifiers
)

def test_phone_number_extraction():
    sample = "Call our officers at +91 90000 00001, 9876543210 or 09123456789 for help."
    phones = extract_phone_numbers(sample)
    assert "+919000000001" in phones
    assert "+919876543210" in phones
    assert "+919123456789" in phones
    assert len(phones) == 3

def test_upi_vs_email_separation():
    sample = "Send fees to support@example.com or use UPI id demo.pay@demoupi. Also contact alert@sbi.co.in or paytm.user@paytm."
    emails = extract_emails(sample)
    upis = extract_upi_ids(sample)

    # Emails have dots in the domain
    assert "support@example.com" in emails
    assert "alert@sbi.co.in" in emails
    assert "demo.pay@demoupi" not in emails
    assert "paytm.user@paytm" not in emails

    # UPI IDs do not have dots in the handle
    assert "demo.pay@demoupi" in upis
    assert "paytm.user@paytm" in upis
    assert "support@example.com" not in upis
    assert "alert@sbi.co.in" not in upis

def test_url_and_domain_extraction():
    sample = "Visit http://demo-scam.test/kyc-portal?id=123 or check www.sbi-fake.test/login immediately."
    data = extract_urls_and_domains(sample)
    domains = data["domains"]
    urls = data["urls"]

    assert "demo-scam.test" in domains
    assert "www.sbi-fake.test" in domains or "sbi-fake.test" in domains
    assert any("demo-scam.test" in u for u in urls)

def test_crypto_wallet_extraction():
    sample = (
        "BTC Legacy: 1SyntheticBtcFakeAddressForDemo99\n"
        "BTC Bech32: bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq\n"
        "ETH: 0x71C7656EC7ab88b098defB751B7401B5f6d8976F\n"
        "TRON: TLyqzVGLV1srkB7dToTAwdg296wc9g32pU"
    )
    wallets = extract_crypto_wallets(sample)
    wallet_values = [w["value"] for w in wallets]

    # BTC Legacy and TRON must retain exact case (case-sensitive)
    assert "1SyntheticBtcFakeAddressForDemo99" in wallet_values
    assert "TLyqzVGLV1srkB7dToTAwdg296wc9g32pU" in wallet_values
    assert "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq" in wallet_values
    # ETH retains original casing for display
    assert "0x71C7656EC7ab88b098defB751B7401B5f6d8976F" in wallet_values

def test_bank_account_and_ifsc():
    sample = "Please deposit fee into account 987654321098 with IFSC code SBIN0001234. Random number 12345."
    data = extract_bank_accounts_and_ifsc(sample)
    assert "987654321098" in data["bank_accounts"]
    assert "SBIN0001234" in data["ifsc_codes"]
    # Ensure random short number not matched as bank account
    assert "12345" not in data["bank_accounts"]

def test_extract_all_identifiers():
    sample = (
        "Urgent: Contact +91 90000 00001 or email officer@cyber.test. "
        "Pay to upi quick.pay@demoupi or visit http://demo-scam.test"
    )
    all_ids = extract_all_identifiers(sample)
    types = {item["type"] for item in all_ids}
    values = {item["value"] for item in all_ids}

    assert "phone" in types
    assert "email" in types
    assert "upi" in types
    assert "url" in types
    assert "domain" in types
    assert "+919000000001" in values
    assert "officer@cyber.test" in values
    assert "quick.pay@demoupi" in values
    assert "demo-scam.test" in values

def test_identifier_normalization_rules():
    raw_text = (
        "Contact OFFICER@CYBER.TEST or UPI DEMO.PAY@DEMOUPI. "
        "Visit HTTP://FAKE-BANK.TEST. "
        "BTC: 1SyntheticBtcFakeAddressForDemo99. "
        "TRON: TLyqzVGLV1srkB7dToTAwdg296wc9g32pU. "
        "ETH: 0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
    )
    all_ids = extract_all_identifiers(raw_text)
    id_map = {item["value"]: item["type"] for item in all_ids}

    # Domains, emails, and UPI must be lowercased
    assert "officer@cyber.test" in id_map
    assert "demo.pay@demoupi" in id_map
    assert "fake-bank.test" in id_map

    # BTC Legacy, TRON, and ETH must NOT be lowercased
    assert "1SyntheticBtcFakeAddressForDemo99" in id_map
    assert "TLyqzVGLV1srkB7dToTAwdg296wc9g32pU" in id_map
    assert "0x71C7656EC7ab88b098defB751B7401B5f6d8976F" in id_map
