from app.security import validate_url_safety, safe_fetch_url, validate_uploaded_file

def test_ssrf_blocks_loopback_ips():
    is_safe, reason, _ = validate_url_safety("http://127.0.0.1/admin")
    assert not is_safe
    assert "loopback" in reason.lower() or "blocked" in reason.lower()

def test_ssrf_blocks_localhost_hostname():
    is_safe, reason, _ = validate_url_safety("http://localhost:8080/secret")
    assert not is_safe
    assert "loopback" in reason.lower() or "blocked" in reason.lower()

    is_safe_sub, _, _ = validate_url_safety("http://app.localhost/api")
    assert not is_safe_sub

def test_ssrf_blocks_private_class_a():
    is_safe, reason, _ = validate_url_safety("http://10.0.0.1/internal")
    assert not is_safe
    assert "private" in reason.lower() or "blocked" in reason.lower()

def test_ssrf_blocks_private_class_c():
    is_safe, reason, _ = validate_url_safety("http://192.168.1.100/router")
    assert not is_safe
    assert "private" in reason.lower() or "blocked" in reason.lower()

def test_ssrf_blocks_link_local_metadata():
    # AWS/GCP/Azure instance metadata endpoint
    is_safe, reason, _ = validate_url_safety("http://169.254.169.254/latest/meta-data/")
    assert not is_safe
    assert "link-local" in reason.lower() or "blocked" in reason.lower()

def test_ssrf_blocks_non_http_schemes():
    for bad_scheme in ["ftp://example.com/file", "file:///etc/passwd", "gopher://evil.com", "ldap://host"]:
        is_safe, reason, _ = validate_url_safety(bad_scheme)
        assert not is_safe
        assert "unsupported scheme" in reason.lower()

def test_safe_fetch_blocks_private_target():
    result = safe_fetch_url("http://127.0.0.1:8000/api/health")
    assert not result["success"]
    assert result["blocked_by_ssrf"] is True
    assert "loopback" in result["error"].lower() or "blocked" in result["error"].lower()

def test_file_upload_validation():
    # Valid html file under 1MB
    valid, _ = validate_uploaded_file("sample.html", 500, b"<html><body>Test</body></html>")
    assert valid is True

    # Valid txt file
    valid_txt, _ = validate_uploaded_file("note.txt", 100, b"plain text")
    assert valid_txt is True

    # Invalid extension
    bad_ext, reason = validate_uploaded_file("malicious.exe", 200, b"MZ...")
    assert bad_ext is False
    assert "unsupported" in reason.lower()

    # Oversized file (> 1 MB)
    large_size = 2 * 1024 * 1024
    too_large, reason_size = validate_uploaded_file("huge.html", large_size, b"x" * 100)
    assert too_large is False
    assert "exceeds" in reason_size.lower()
