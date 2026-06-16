"""Business logic for interview sessions and answer evaluation."""

from app.core.exceptions import NotFoundError
from app.models.enums import InterviewStatus
from app.models.interview import Analytics, Answer, Evaluation, InterviewSession, Question
from app.repositories.interview_repository import InterviewRepository
from app.schemas.interview import AnswerSubmit, InterviewCreate
from app.services.ai_service import AIService


class InterviewService:
    def __init__(self, interviews: InterviewRepository, ai: AIService) -> None:
        self.interviews = interviews
        self.ai = ai

    async def create_session(self, user_id: int, payload: InterviewCreate) -> InterviewSession:
        generated = await self.ai.generate_questions(payload.role, payload.question_count)
        questions = [
            Question(
                prompt=item.get("prompt", "Explain a production-grade solution."),
                skill=item.get("skill", payload.role.value),
                difficulty=item.get("difficulty", "medium"),
            )
            for item in generated[: payload.question_count]
        ]
        session = InterviewSession(user_id=user_id, role=payload.role, title=f"{payload.role.value} practice")
        return await self.interviews.create_session(session, questions)

    async def get_session(self, session_id: int, user_id: int) -> InterviewSession:
        session = await self.interviews.get_session(session_id, user_id)
        if not session:
            raise NotFoundError("Interview session not found")
        return session

    async def submit_answer(self, user_id: int, question_id: int, payload: AnswerSubmit) -> Answer:
        question = await self.interviews.get_question_for_user(question_id, user_id)
        if not question:
            raise NotFoundError("Question not found")
        result = await self.ai.evaluate_answer(question.prompt, payload.content)
        score = min(10.0, max(1.0, float(result.get("score", 1))))
        answer = Answer(question_id=question_id, user_id=user_id, content=payload.content)
        evaluation = Evaluation(
            score=score,
            strengths=list(result.get("strengths", [])),
            weaknesses=list(result.get("weaknesses", [])),
            suggestions=list(result.get("suggestions", [])),
        )
        saved = await self.interviews.create_answer_with_evaluation(answer, evaluation)
        await self._refresh_session_analytics(question.session_id, user_id)
        return saved

    async def _refresh_session_analytics(self, session_id: int, user_id: int) -> None:
        scores = await self.interviews.scores_by_user(user_id)
        if not scores:
            return
        skill_totals: dict[str, list[float]] = {}
        for score, skill in scores:
            skill_totals.setdefault(skill, []).append(float(score))
        skill_breakdown = {
            skill: round(sum(values) / len(values), 2) for skill, values in skill_totals.items()
        }
        average = round(sum(score for score, _ in scores) / len(scores), 2)
        await self.interviews.save_analytics(
            Analytics(user_id=user_id, session_id=session_id, average_score=average, skill_breakdown=skill_breakdown)
        )
