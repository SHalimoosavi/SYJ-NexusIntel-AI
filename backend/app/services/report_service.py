import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from app.services.intelligence_service import (
    generate_intelligence_report
)

from app.services.technology_service import (
    detect_technologies
)

from app.services.lead_qualification_service import (
    qualify_lead
)


REPORTS_DIR = "reports"

os.makedirs(
    REPORTS_DIR,
    exist_ok=True
)


def generate_pdf_report(domain: str):

    intelligence = (
        generate_intelligence_report(
            domain
        )
    )

    technology = (
        detect_technologies(
            domain
        )
    )

    qualification = (
        qualify_lead(
            domain
        )
    )

    pdf_file = (
        f"{REPORTS_DIR}/{domain}.pdf"
    )

    document = SimpleDocTemplate(
        pdf_file
    )

    styles = (
        getSampleStyleSheet()
    )

    content = []

    content.append(
        Paragraph(
            f"SYJ NexusIntel AI Report - {domain}",
            styles["Title"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    content.append(
        Paragraph(
            f"Overall Score: "
            f"{intelligence['overall_score']}",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            f"Security Score: "
            f"{intelligence['security_score']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"SEO Score: "
            f"{intelligence['seo_score']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Trust Score: "
            f"{intelligence['trust_score']}",
            styles["Normal"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    content.append(
        Paragraph(
            f"Lead Priority: "
            f"{qualification['priority']}",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            qualification[
                "sales_recommendation"
            ],
            styles["Normal"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    content.append(
        Paragraph(
            "Technologies",
            styles["Heading2"]
        )
    )

    technologies = (
        technology.get(
            "technologies",
            []
        )
    )

    if technologies:

        for tech in technologies:

            content.append(
                Paragraph(
                    f"- {tech}",
                    styles["Normal"]
                )
            )

    else:

        content.append(
            Paragraph(
                "No technologies detected",
                styles["Normal"]
            )
        )

    content.append(
        Spacer(1, 20)
    )

    content.append(
        Paragraph(
            "Recommendations",
            styles["Heading2"]
        )
    )

    for recommendation in (
        intelligence[
            "recommendations"
        ]
    ):

        content.append(
            Paragraph(
                f"- {recommendation}",
                styles["Normal"]
            )
        )

    document.build(content)

    return {
        "success": True,
        "pdf_path": pdf_file
    }
