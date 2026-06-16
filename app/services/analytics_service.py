"""Business logic for aggregate interview analytics."""

from app.repositories.interview_repository import InterviewRepository
from app.schemas.analytics import AnalyticsSummary


class AnalyticsService:
    def __init__(self, interviews: InterviewRepository) -> None:
        self.interviews = interviews

    async def summary(self, user_id: int) -> AnalyticsSummary:
        total_interviews = await self.interviews.total_sessions_by_user(user_id)
        scores = await self.interviews.scores_by_user(user_id)
        if not scores:
            return AnalyticsSummary(
                total_interviews=total_interviews,
                average_score=0.0,
                improvement_trend=[],
                skill_breakdown={},
            )
        trend = [round(float(score), 2) for score, _ in scores]
        average = round(sum(trend) / len(trend), 2)
        grouped: dict[str, list[float]] = {}
        for score, skill in scores:
            grouped.setdefault(skill, []).append(float(score))
        skill_breakdown = {skill: round(sum(values) / len(values), 2) for skill, values in grouped.items()}
        return AnalyticsSummary(
            total_interviews=total_interviews,
            average_score=average,
            improvement_trend=trend,
            skill_breakdown=skill_breakdown,
        )
