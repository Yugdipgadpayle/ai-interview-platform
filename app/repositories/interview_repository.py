"""Repository for interview sessions, questions, answers, evaluations, and analytics."""

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interview import Analytics, Answer, Evaluation, InterviewSession, Question


class InterviewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(self, session: InterviewSession, questions: list[Question]) -> InterviewSession:
        session.questions = questions
        self.db.add(session)
        await self.db.commit()
        return await self.get_session(session.id, session.user_id)  # type: ignore[return-value]

    async def get_session(self, session_id: int, user_id: int | None = None) -> InterviewSession | None:
        query: Select[tuple[InterviewSession]] = (
            select(InterviewSession)
            .options(selectinload(InterviewSession.questions))
            .where(InterviewSession.id == session_id)
        )
        if user_id is not None:
            query = query.where(InterviewSession.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_sessions(self, user_id: int, offset: int, limit: int) -> tuple[list[InterviewSession], int]:
        query = (
            select(InterviewSession)
            .options(selectinload(InterviewSession.questions))
            .where(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        count_query = select(func.count()).select_from(InterviewSession).where(InterviewSession.user_id == user_id)
        rows = (await self.db.execute(query)).scalars().all()
        total = (await self.db.execute(count_query)).scalar_one()
        return list(rows), total

    async def get_question_for_user(self, question_id: int, user_id: int) -> Question | None:
        query = (
            select(Question)
            .join(InterviewSession)
            .where(Question.id == question_id, InterviewSession.user_id == user_id)
        )
        return (await self.db.execute(query)).scalar_one_or_none()

    async def create_answer_with_evaluation(self, answer: Answer, evaluation: Evaluation) -> Answer:
        answer.evaluation = evaluation
        self.db.add(answer)
        await self.db.commit()
        await self.db.refresh(answer, attribute_names=["evaluation"])
        return answer

    async def save_analytics(self, analytics: Analytics) -> Analytics:
        existing = (
            await self.db.execute(select(Analytics).where(Analytics.session_id == analytics.session_id))
        ).scalar_one_or_none()
        if existing:
            existing.average_score = analytics.average_score
            existing.skill_breakdown = analytics.skill_breakdown
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        self.db.add(analytics)
        await self.db.commit()
        await self.db.refresh(analytics)
        return analytics

    async def scores_by_user(self, user_id: int) -> list[tuple[float, str]]:
        query = (
            select(Evaluation.score, Question.skill)
            .join(Answer, Answer.id == Evaluation.answer_id)
            .join(Question, Question.id == Answer.question_id)
            .where(Answer.user_id == user_id)
            .order_by(Evaluation.created_at.asc())
        )
        return list((await self.db.execute(query)).all())

    async def total_sessions_by_user(self, user_id: int) -> int:
        query = select(func.count()).select_from(InterviewSession).where(InterviewSession.user_id == user_id)
        return (await self.db.execute(query)).scalar_one()
