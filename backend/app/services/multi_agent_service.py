from app.services.intelligence_service import (
    generate_intelligence_report
)

from app.services.opportunity_service import (
    analyze_opportunity
)

from app.services.sales_agent_service import (
    generate_pitch
)

from app.services.agent_memory_service import (
    save_memory
)


def generate_executive_summary(
    intelligence,
    opportunity
):

    score = intelligence.get(
        "overall_score",
        0
    )

    value = opportunity.get(
        "estimated_project_value",
        "Unknown"
    )

    if score < 60:

        recommendation = (
            "High optimization opportunity detected."
        )

    else:

        recommendation = (
            "Maintain performance and pursue upsell opportunities."
        )

    return {
        "executive_summary":
        (
            f"Lead scored {score}/100. "
            f"Estimated project value {value}."
        ),

        "recommendation":
        recommendation
    }


def run_multi_agent_analysis(
    domain: str,
    db
):

    intelligence = (
        generate_intelligence_report(
            domain
        )
    )

    opportunity = (
        analyze_opportunity(
            domain
        )
    )

    sales = (
        generate_pitch(
            business_name=domain,
            domain=domain,
            lead_score=intelligence.get(
                "overall_score",
                0
            )
        )
    )

    executive = (
        generate_executive_summary(
            intelligence,
            opportunity
        )
    )

    memory_payload = {

        "domain":
        domain,

        "overall_score":
        intelligence.get(
            "overall_score",
            0
        ),

        "priority":
        sales.get(
            "priority",
            "UNKNOWN"
        ),

        "estimated_value":
        opportunity.get(
            "estimated_project_value",
            ""
        ),

        "analysis_data":
        str({
            "research_agent":
            intelligence,

            "opportunity_agent":
            opportunity,

            "sales_agent":
            sales,

            "executive_agent":
            executive
        })
    }

    save_memory(
        db,
        memory_payload
    )

    return {

        "research_agent":
        intelligence,

        "opportunity_agent":
        opportunity,

        "sales_agent":
        sales,

        "executive_agent":
        executive,

        "memory_saved":
        True
    }
