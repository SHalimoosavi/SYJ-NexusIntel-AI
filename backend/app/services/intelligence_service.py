from app.services.osint_service import (
    get_ssl_info,
    get_security_headers,
    get_seo_data
)


def calculate_security_score(headers, ssl_info):

    score = 0

    if ssl_info.get("valid"):
        score += 40

    if headers.get("hsts"):
        score += 20

    if headers.get("csp"):
        score += 20

    if headers.get("x_frame_options"):
        score += 10

    if headers.get("x_content_type_options"):
        score += 10

    return min(score, 100)


def calculate_seo_score(seo):

    score = 0

    title = seo.get("title", "")
    description = seo.get("description", "")
    h1_count = seo.get("h1_count", 0)

    if title:
        score += 40

    if description:
        score += 40

    if h1_count > 0:
        score += 20

    return min(score, 100)


def calculate_trust_score(
    ssl_score,
    security_score
):

    score = (
        ssl_score +
        security_score
    ) // 2

    return min(score, 100)


def generate_recommendations(
    headers,
    seo,
    ssl_info
):

    recommendations = []

    if not ssl_info.get("valid"):
        recommendations.append(
            "Enable SSL certificate"
        )

    if not headers.get("hsts"):
        recommendations.append(
            "Enable HSTS security header"
        )

    if not headers.get("csp"):
        recommendations.append(
            "Add Content Security Policy"
        )

    if not seo.get("description"):
        recommendations.append(
            "Add meta description"
        )

    if seo.get("h1_count", 0) == 0:
        recommendations.append(
            "Add at least one H1 tag"
        )

    return recommendations


def generate_intelligence_report(domain):

    ssl_info = get_ssl_info(domain)

    headers = get_security_headers(domain)

    seo = get_seo_data(domain)

    security_score = calculate_security_score(
        headers,
        ssl_info
    )

    seo_score = calculate_seo_score(
        seo
    )

    trust_score = calculate_trust_score(
        100 if ssl_info.get("valid") else 0,
        security_score
    )

    overall_score = (
        security_score +
        seo_score +
        trust_score
    ) // 3

    recommendations = generate_recommendations(
        headers,
        seo,
        ssl_info
    )

    return {
        "domain": domain,
        "overall_score": overall_score,
        "security_score": security_score,
        "seo_score": seo_score,
        "trust_score": trust_score,
        "recommendations": recommendations
    }
