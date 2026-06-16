"""Analytics endpoints."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_analytics_service, get_current_user
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def analytics_summary(
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsSummary:
    return await service.summary(current_user.id)
