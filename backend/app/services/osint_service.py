import socket
import ssl

import dns.resolver
from bs4 import BeautifulSoup

from app.core.safe_http import assert_public_domain, resolve_public_addresses, safe_get


def get_whois(domain: str):
    try:
        from whois import whois
        host = assert_public_domain(domain)
        data = whois(host)
        return {
            "registrar": str(data.registrar),
            "creation_date": str(data.creation_date),
            "expiration_date": str(data.expiration_date),
        }
    except Exception:
        return {"error": "WHOIS lookup failed for the supplied public domain"}


def get_dns(domain: str):
    try:
        host = assert_public_domain(domain)
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
        answers = resolver.resolve(host, "A", lifetime=5)
        result = [record.to_text() for record in answers]
        for address in result:
            import ipaddress
            if not ipaddress.ip_address(address).is_global:
                raise ValueError("Non-public DNS answer rejected")
        return result
    except Exception:
        return {"error": "DNS lookup failed or returned a non-public address"}


def get_ip(domain: str):
    try:
        _host, addresses = resolve_public_addresses(domain)
        return addresses[0]
    except Exception:
        return None


def get_ssl_info(domain: str):
    try:
        host, addresses = resolve_public_addresses(domain)
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=host) as sock:
            sock.settimeout(5)
            sock.connect((addresses[0], 443))
            cert = sock.getpeercert()
        return {"valid": True, "issuer": str(cert.get("issuer"))}
    except Exception:
        return {"valid": False, "error": "TLS inspection failed for public domain"}


def get_security_headers(domain: str):
    try:
        response = safe_get(domain, timeout=10)
        try:
            headers = response.headers
            return {
                "hsts": "Strict-Transport-Security" in headers,
                "csp": "Content-Security-Policy" in headers,
                "x_frame_options": "X-Frame-Options" in headers,
                "x_content_type_options": "X-Content-Type-Options" in headers,
            }
        finally:
            response.close()
    except Exception:
        return {"error": "Security header inspection failed for public domain"}


def get_seo_data(domain: str):
    try:
        response = safe_get(domain, timeout=10)
        try:
            soup = BeautifulSoup(response.text, "lxml")
            title = soup.title.text if soup.title else ""
            meta = soup.select_one('meta[name="description"]')
            description = meta.get("content", "") if meta is not None else ""
            return {
                "title": title,
                "description": description,
                "h1_count": len(soup.find_all("h1")),
            }
        finally:
            response.close()
    except Exception:
        return {"error": "SEO inspection failed for public domain"}
