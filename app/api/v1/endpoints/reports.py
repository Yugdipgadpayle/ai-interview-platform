"""PDF report endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.api.dependencies import get_analytics_service, get_current_user, get_report_service
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/interview.pdf", response_class=Response)
async def interview_report(
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    report_service: ReportService = Depends(get_report_service),
) -> Response:
    analytics = await analytics_service.summary(current_user.id)
    pdf = report_service.build_interview_report(current_user.full_name, analytics)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="interview-report.pdf"'},
    )
