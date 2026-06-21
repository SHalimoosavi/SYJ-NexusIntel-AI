from app.services.intelligence_service import (
    generate_intelligence_report
)


def determine_project_value(score: int):

    if score >= 80:
        return "$5,000 - $15,000"

    if score >= 60:
        return "$2,000 - $5,000"

    if score >= 40:
        return "$1,000 - $2,000"

    return "$300 - $1,000"


def determine_priority(score: int):

    if score >= 80:
        return "HOT"

    if score >= 60:
        return "WARM"

    return "COLD"


def determine_services(report):

    services = []

    recommendations = report.get(
        "recommendations",
        []
    )

    recommendation_text = (
        " ".join(recommendations)
    ).lower()

    if (
        "seo" in recommendation_text
        or
        "meta" in recommendation_text
        or
        "h1" in recommendation_text
    ):
        services.append(
            "SEO Optimization"
        )

    if (
        "security" in recommendation_text
        or
        "hsts" in recommendation_text
        or
        "content security policy"
        in recommendation_text
    ):
        services.append(
            "Security Hardening"
        )

    services.append(
        "Website Audit"
    )

    services.append(
        "Business Intelligence"
    )

    return list(
        set(services)
    )


def create_sales_pitch(
    domain: str,
    score: int
):

    return (
        f"{domain} currently has "
        f"an optimization score of {score}. "
        f"We identified opportunities "
        f"to improve visibility, security "
        f"and digital performance."
    )


def analyze_opportunity(
    domain: str,
):

    report = (
        generate_intelligence_report(
            domain
        )
    )

    score = report.get(
        "overall_score",
        0
    )

    services = determine_services(
        report
    )

    return {
        "domain": domain,

        "lead_score": score,

        "estimated_project_value":
        determine_project_value(
            score
        ),

        "priority":
        determine_priority(
            score
        ),

        "service_opportunities":
        services,

        "revenue_potential":
        determine_project_value(
            score
        ),

        "sales_pitch":
        create_sales_pitch(
            domain,
            score
        )
    }
