import os
import uuid
from html import escape
from pathlib import Path

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.services.intelligence_service import generate_intelligence_report
from app.services.lead_qualification_service import qualify_lead
from app.services.technology_service import detect_technologies

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "/tmp/nexusintel-reports")).resolve()
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_pdf_report(domain: str):
    intelligence = generate_intelligence_report(domain)
    technology = detect_technologies(domain)
    qualification = qualify_lead(domain)

    # Never derive a filesystem path from user-controlled input.
    report_path = (REPORTS_DIR / f"{uuid.uuid4().hex}.pdf").resolve()
    if report_path.parent != REPORTS_DIR:
        raise ValueError("Invalid report output path")

    document = SimpleDocTemplate(str(report_path))
    styles = getSampleStyleSheet()
    safe_domain = escape(domain)
    content = [
        Paragraph(f"SYJ NexusIntel AI Report - {safe_domain}", styles["Title"]),
        Spacer(1, 20),
        Paragraph(f"Overall Score: {intelligence['overall_score']}", styles["Heading2"]),
        Paragraph(f"Security Score: {intelligence['security_score']}", styles["Normal"]),
        Paragraph(f"SEO Score: {intelligence['seo_score']}", styles["Normal"]),
        Paragraph(f"Trust Score: {intelligence['trust_score']}", styles["Normal"]),
        Spacer(1, 20),
        Paragraph(f"Lead Priority: {escape(str(qualification['priority']))}", styles["Heading2"]),
        Paragraph(escape(str(qualification["sales_recommendation"])), styles["Normal"]),
        Spacer(1, 20),
        Paragraph("Technologies", styles["Heading2"]),
    ]

    technologies = technology.get("technologies", [])
    if technologies:
        for tech in technologies:
            content.append(Paragraph(escape(str(tech)), styles["Normal"]))
    else:
        content.append(Paragraph("No technologies detected", styles["Normal"]))

    content.extend([Spacer(1, 20), Paragraph("Recommendations", styles["Heading2"])])
    for recommendation in intelligence.get("recommendations", []):
        content.append(Paragraph(escape(str(recommendation)), styles["Normal"]))

    document.build(content)
    return {"success": True, "report_id": report_path.stem}
