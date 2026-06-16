"""Interview workflow request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import InterviewRole, InterviewStatus


class QuestionRead(BaseModel):
    id: int
    prompt: str
    skill: str
    difficulty: str

    model_config = {"from_attributes": True}


class InterviewCreate(BaseModel):
    role: InterviewRole
    question_count: int = Field(default=5, ge=1, le=10)


class InterviewRead(BaseModel):
    id: int
    title: str
    role: InterviewRole
    status: InterviewStatus
    created_at: datetime
    completed_at: datetime | None = None
    questions: list[QuestionRead] = []

    model_config = {"from_attributes": True}


class AnswerSubmit(BaseModel):
    content: str = Field(min_length=10, max_length=10_000)


class EvaluationRead(BaseModel):
    id: int
    score: float = Field(ge=1, le=10)
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]

    model_config = {"from_attributes": True}


class AnswerRead(BaseModel):
    id: int
    question_id: int
    content: str
    evaluation: EvaluationRead

    model_config = {"from_attributes": True}
