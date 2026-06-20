from app.services.intelligence_service import (
    generate_intelligence_report
)

from app.services.technology_service import (
    detect_technologies
)


def classify_lead(score: int):

    if score >= 80:
        return "HOT"

    if score >= 50:
        return "WARM"

    return "COLD"


def generate_sales_recommendation(
    score: int,
    technologies: list
):

    if score < 50:

        return (
            "Strong sales opportunity. "
            "Website requires significant "
            "improvements."
        )

    if score < 80:

        return (
            "Moderate opportunity. "
            "Offer SEO and optimization "
            "services."
        )

    return (
        "Low urgency prospect. "
        "Position premium consulting "
        "and monitoring services."
    )


def qualify_lead(domain: str):

    intelligence = generate_intelligence_report(
        domain
    )

    technology_data = detect_technologies(
        domain
    )

    score = intelligence.get(
        "overall_score",
        0
    )

    technologies = technology_data.get(
        "technologies",
        []
    )

    priority = classify_lead(
        score
    )

    recommendation = (
        generate_sales_recommendation(
            score,
            technologies
        )
    )

    return {
        "domain": domain,
        "lead_score": score,
        "priority": priority,
        "technologies": technologies,
        "recommendations":
            intelligence.get(
                "recommendations",
                []
            ),
        "sales_recommendation":
            recommendation
    }
