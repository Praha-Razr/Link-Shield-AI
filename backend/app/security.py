import ipaddress
import socket
import urllib.parse
from typing import Optional, Tuple
import http.client
from app.config import settings

def is_ip_blocked(ip_str: str) -> Tuple[bool, str]:
    """
    Checks if an IP address string belongs to private, loopback, link-local,
    multicast, or reserved address spaces (SSRF protection).
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.is_loopback:
            return True, f"Loopback IP ({ip_str}) is blocked"
        if ip.is_private:
            return True, f"Private network IP ({ip_str}) is blocked"
        if ip.is_link_local:
            return True, f"Link-local IP ({ip_str}) is blocked"
        if ip.is_multicast:
            return True, f"Multicast IP ({ip_str}) is blocked"
        if ip.is_reserved:
            return True, f"Reserved IP ({ip_str}) is blocked"
        if ip.is_unspecified:
            return True, f"Unspecified IP ({ip_str}) is blocked"
        return False, ""
    except ValueError:
        return True, f"Invalid IP address format: {ip_str}"

def validate_url_safety(url_str: str, resolve_dns: bool = True) -> Tuple[bool, str, Optional[str]]:
    """
    Validates a URL before any network request:
    - Scheme must be http or https
    - Hostname must be present
    - Hostname must not be loopback or private IP literal
    - Optional DNS resolution check (when resolve_dns=True): resolved IP must not be private/loopback/reserved
    Returns: (is_safe, reason, resolved_ip)
    """
    parsed = urllib.parse.urlsplit(url_str)
    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        return False, f"Unsupported scheme '{scheme}'. Only http and https are permitted.", None

    hostname = parsed.hostname
    if not hostname:
        return False, "URL does not contain a valid hostname.", None

    hostname_clean = hostname.lower().strip()
    if hostname_clean in ("localhost", "127.0.0.1", "0.0.0.0", "::1", "::"):
        return False, f"Host '{hostname_clean}' is a loopback address and is blocked.", None

    if hostname_clean.endswith(".localhost"):
        return False, f"Host '{hostname_clean}' is a local domain and is blocked.", None

    # Check if hostname itself is an IP literal
    try:
        ip = ipaddress.ip_address(hostname_clean)
        blocked, reason = is_ip_blocked(str(ip))
        if blocked:
            return False, f"Direct IP access blocked: {reason}", str(ip)
        return True, "Valid public IP", str(ip)
    except ValueError:
        pass  # It's a regular domain name, will resolve below if requested

    # If static check only (resolve_dns=False), don't perform live DNS resolution
    if not resolve_dns:
        return True, "Valid hostname syntax (static analysis)", None

    # Resolve hostname to IPv4/IPv6
    try:
        addr_info = socket.getaddrinfo(hostname_clean, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        if not addr_info:
            return False, f"Could not resolve hostname '{hostname_clean}'.", None

        # Inspect all resolved IPs; if any is private/blocked, reject the host
        for entry in addr_info:
            ip_str = entry[4][0]
            blocked, reason = is_ip_blocked(ip_str)
            if blocked:
                return False, f"DNS resolved to prohibited address ({ip_str}): {reason}", ip_str

        # Pick the first resolved IP
        primary_ip = addr_info[0][4][0]
        return True, "Host is public and valid", primary_ip
    except socket.gaierror as e:
        return False, f"DNS resolution failed for '{hostname_clean}': {str(e)}", None
    except Exception as e:
        return False, f"Error validating host '{hostname_clean}': {str(e)}", None

def safe_fetch_url(url: str) -> dict:
    """
    Performs SSRF-safe URL fetching with:
    - Scheme restrictions (http/https)
    - Manual redirect following (max 5 hops)
    - DNS re-validation at every hop
    - 5-second timeout
    - 2 MB response size cap
    - Returns structured metadata and raw body (string/bytes)
    """
    current_url = url
    hops = []
    
    for hop_idx in range(settings.MAX_REDIRECT_HOPS + 1):
        is_safe, reason, resolved_ip = validate_url_safety(current_url)
        if not is_safe:
            return {
                "success": False,
                "error": reason,
                "final_url": current_url,
                "redirect_chain": hops,
                "status_code": None,
                "content": "",
                "resolved_ip": resolved_ip,
                "blocked_by_ssrf": "blocked" in reason.lower() or "prohibited" in reason.lower() or "loopback" in reason.lower()
            }

        hops.append({"url": current_url, "resolved_ip": resolved_ip})

        parsed = urllib.parse.urlsplit(current_url)
        scheme = parsed.scheme.lower()
        port = parsed.port or (443 if scheme == "https" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"

        try:
            if scheme == "https":
                conn = http.client.HTTPSConnection(
                    parsed.hostname,
                    port=port,
                    timeout=settings.HTTP_TIMEOUT_SECONDS
                )
            else:
                conn = http.client.HTTPConnection(
                    parsed.hostname,
                    port=port,
                    timeout=settings.HTTP_TIMEOUT_SECONDS
                )

            headers = {
                "User-Agent": "LinkShield-Static-Inspector/1.0 (+https://linkshield.test/bot)",
                "Accept": "text/html,text/plain,application/xhtml+xml;q=0.9,*/*;q=0.8",
                "Connection": "close"
            }
            conn.request("GET", path, headers=headers)
            response = conn.getresponse()
            status = response.status

            # Handle redirects manually
            if status in (301, 302, 303, 307, 308):
                redirect_location = response.getheader("Location")
                conn.close()
                if not redirect_location:
                    return {
                        "success": False,
                        "error": f"Received redirect status {status} but no Location header.",
                        "final_url": current_url,
                        "redirect_chain": hops,
                        "status_code": status,
                        "content": "",
                        "resolved_ip": resolved_ip,
                        "blocked_by_ssrf": False
                    }
                # Resolve relative redirect URLs
                next_url = urllib.parse.urljoin(current_url, redirect_location)
                current_url = next_url
                continue

            # Read response body capped at MAX_RESPONSE_BYTES
            body_bytes = response.read(settings.MAX_RESPONSE_BYTES + 1)
            conn.close()

            if len(body_bytes) > settings.MAX_RESPONSE_BYTES:
                return {
                    "success": False,
                    "error": f"Response exceeded maximum allowed size of {settings.MAX_RESPONSE_BYTES} bytes.",
                    "final_url": current_url,
                    "redirect_chain": hops,
                    "status_code": status,
                    "content": "",
                    "resolved_ip": resolved_ip,
                    "blocked_by_ssrf": False
                }

            # Decode body
            encoding = response.getheader("Content-Type", "")
            charset = "utf-8"
            if "charset=" in encoding.lower():
                try:
                    charset = encoding.lower().split("charset=")[-1].split(";")[0].strip()
                except Exception:
                    charset = "utf-8"

            try:
                decoded_text = body_bytes.decode(charset, errors="replace")
            except Exception:
                decoded_text = body_bytes.decode("utf-8", errors="replace")

            return {
                "success": True,
                "error": None,
                "final_url": current_url,
                "redirect_chain": hops,
                "status_code": status,
                "headers": dict(response.getheaders()),
                "content": decoded_text,
                "resolved_ip": resolved_ip,
                "blocked_by_ssrf": False
            }

        except (socket.timeout, TimeoutError):
            return {
                "success": False,
                "error": f"Connection timed out after {settings.HTTP_TIMEOUT_SECONDS}s.",
                "final_url": current_url,
                "redirect_chain": hops,
                "status_code": None,
                "content": "",
                "resolved_ip": resolved_ip,
                "blocked_by_ssrf": False
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Network fetch failed: {str(e)}",
                "final_url": current_url,
                "redirect_chain": hops,
                "status_code": None,
                "content": "",
                "resolved_ip": resolved_ip,
                "blocked_by_ssrf": False
            }

    return {
        "success": False,
        "error": f"Exceeded maximum redirect limit of {settings.MAX_REDIRECT_HOPS} hops.",
        "final_url": current_url,
        "redirect_chain": hops,
        "status_code": None,
        "content": "",
        "resolved_ip": None,
        "blocked_by_ssrf": False
    }

def validate_uploaded_file(filename: str, file_size: int, content_bytes: bytes) -> Tuple[bool, str]:
    """
    Validates uploaded file:
    - Extensions allowed: .html, .htm, .txt
    - Size cap: max 1 MB
    - No execution, static content only
    """
    if file_size > settings.MAX_FILE_UPLOAD_BYTES or len(content_bytes) > settings.MAX_FILE_UPLOAD_BYTES:
        return False, f"File size exceeds 1 MB limit (size: {file_size} bytes)."

    lower_name = filename.lower()
    allowed_exts = (".html", ".htm", ".txt")
    if not any(lower_name.endswith(ext) for ext in allowed_exts):
        return False, f"Unsupported file extension. Only .html, .htm, and .txt files are allowed."

    return True, "File is valid"
