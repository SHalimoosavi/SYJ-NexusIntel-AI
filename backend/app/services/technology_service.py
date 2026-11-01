from app.core.safe_http import safe_get


def detect_technologies(domain: str):

    technologies = []

    try:

        response = safe_get(domain, timeout=10)

        html = response.text.lower()

        headers = response.headers

        server = headers.get(
            "server",
            ""
        ).lower()

        powered_by = headers.get(
            "x-powered-by",
            ""
        ).lower()

        if "wordpress" in html:
            technologies.append(
                "WordPress"
            )

        if "wp-content" in html:
            technologies.append(
                "WordPress"
            )

        if "shopify" in html:
            technologies.append(
                "Shopify"
            )

        if "_next" in html:
            technologies.append(
                "Next.js"
            )

        if "__next" in html:
            technologies.append(
                "Next.js"
            )

        if "react" in html:
            technologies.append(
                "React"
            )

        if "jquery" in html:
            technologies.append(
                "jQuery"
            )

        if "bootstrap" in html:
            technologies.append(
                "Bootstrap"
            )

        if "cloudflare" in str(headers).lower():
            technologies.append(
                "Cloudflare"
            )

        if "nginx" in server:
            technologies.append(
                "Nginx"
            )

        if "apache" in server:
            technologies.append(
                "Apache"
            )

        if "laravel" in powered_by:
            technologies.append(
                "Laravel"
            )

        if "django" in powered_by:
            technologies.append(
                "Django"
            )

        response.close()

        return {
            "domain": domain,
            "technologies": list(set(technologies))
        }

    except Exception:
        return {
            "domain": domain,
            "technologies": [],
            "error": "Technology inspection failed for public domain"
        }
