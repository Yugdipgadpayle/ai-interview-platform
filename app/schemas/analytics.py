"""Analytics response schemas."""

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_interviews: int
    average_score: float
    improvement_trend: list[float]
    skill_breakdown: dict[str, float]
