"""PDF report generation using ReportLab."""

from io import BytesIO

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.schemas.analytics import AnalyticsSummary


class ReportService:
    def build_interview_report(self, user_name: str, analytics: AnalyticsSummary) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=LETTER, title="Interview Practice Report")
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Interview Practice Report", styles["Title"]),
            Paragraph(f"Candidate: {user_name}", styles["Normal"]),
            Spacer(1, 12),
            Paragraph(f"Total interviews: {analytics.total_interviews}", styles["Normal"]),
            Paragraph(f"Average score: {analytics.average_score}", styles["Normal"]),
            Spacer(1, 12),
            Paragraph("Skill Breakdown", styles["Heading2"]),
        ]
        if analytics.skill_breakdown:
            for skill, score in analytics.skill_breakdown.items():
                story.append(Paragraph(f"{skill}: {score}", styles["Normal"]))
        else:
            story.append(Paragraph("No evaluated answers yet.", styles["Normal"]))
        story.extend([Spacer(1, 12), Paragraph("Recommendations", styles["Heading2"])])
        story.append(Paragraph("Practice concise STAR answers and add measurable production trade-offs.", styles["Normal"]))
        doc.build(story)
        return buffer.getvalue()
