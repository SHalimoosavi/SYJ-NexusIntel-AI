import socket
import ssl

import dns.resolver
import requests
import whois

from bs4 import BeautifulSoup


def get_whois(domain: str):
    try:
        data = whois.whois(domain)

        return {
            "registrar": str(data.registrar),
            "creation_date": str(data.creation_date),
            "expiration_date": str(data.expiration_date)
        }

    except Exception as e:
        return {
            "error": str(e)
        }


def get_dns(domain: str):
    try:
        resolver = dns.resolver.Resolver()

        resolver.nameservers = [
            "8.8.8.8",
            "1.1.1.1"
        ]

        answers = resolver.resolve(
            domain,
            "A"
        )

        return [
            record.to_text()
            for record in answers
        ]

    except Exception as e:
        return {
            "error": str(e)
        }


def get_ip(domain: str):
    try:
        return socket.gethostbyname(domain)

    except Exception:
        return None


def get_ssl_info(domain: str):
    try:
        context = ssl.create_default_context()

        with context.wrap_socket(
            socket.socket(),
            server_hostname=domain
        ) as sock:

            sock.settimeout(5)

            sock.connect((domain, 443))

            cert = sock.getpeercert()

            return {
                "valid": True,
                "issuer": str(
                    cert.get("issuer")
                )
            }

    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


def get_security_headers(domain: str):
    try:
        response = requests.get(
            f"https://{domain}",
            timeout=10
        )

        headers = response.headers

        return {
            "hsts": "Strict-Transport-Security" in headers,
            "csp": "Content-Security-Policy" in headers,
            "x_frame_options": "X-Frame-Options" in headers,
            "x_content_type_options":
                "X-Content-Type-Options" in headers
        }

    except Exception as e:
        return {
            "error": str(e)
        }


def get_seo_data(domain: str):
    try:
        response = requests.get(
            f"https://{domain}",
            timeout=10
        )

        soup = BeautifulSoup(
            response.text,
            "lxml"
        )

        title = ""

        if soup.title:
            title = soup.title.text

        description = ""

        meta = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        if meta:
            description = meta.get(
                "content",
                ""
            )

        h1_count = len(
            soup.find_all("h1")
        )

        return {
            "title": title,
            "description": description,
            "h1_count": h1_count
        }

    except Exception as e:
        return {
            "error": str(e)
        }
