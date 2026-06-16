"""AI provider abstraction for question generation and answer evaluation."""

import json
import logging
from typing import Protocol

from app.models.enums import InterviewRole

logger = logging.getLogger(__name__)


class AIService(Protocol):
    async def generate_questions(self, role: InterviewRole, count: int) -> list[dict[str, str]]:
        ...

    async def evaluate_answer(self, question: str, answer: str) -> dict[str, object]:
        ...


class MockAIService:
    async def generate_questions(self, role: InterviewRole, count: int) -> list[dict[str, str]]:
        templates = {
            InterviewRole.FRONTEND: ("React state management", "Explain how you prevent unnecessary re-renders."),
            InterviewRole.BACKEND: ("API design", "Design a rate-limited REST API for a high-traffic service."),
            InterviewRole.FULL_STACK: ("System design", "Describe how you would build a real-time dashboard."),
            InterviewRole.DATA_SCIENCE: ("Model evaluation", "Explain how you would handle class imbalance."),
        }
        skill, prompt = templates[role]
        return [
            {
                "prompt": f"{prompt} Include trade-offs and production concerns. Question {index + 1}.",
                "skill": skill,
                "difficulty": "medium",
            }
            for index in range(count)
        ]

    async def evaluate_answer(self, question: str, answer: str) -> dict[str, object]:
        length_score = min(10, max(1, len(answer.split()) // 18 + 3))
        return {
            "score": float(length_score),
            "strengths": ["Provides a structured response", "Addresses the question directly"],
            "weaknesses": ["Could include more concrete metrics", "Could discuss failure modes in more detail"],
            "suggestions": ["Add a brief architecture diagram verbally", "Mention observability and testing strategy"],
        }


class OpenAIService(MockAIService):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def _client(self):
        from openai import AsyncOpenAI

        return AsyncOpenAI(api_key=self.api_key)

    async def generate_questions(self, role: InterviewRole, count: int) -> list[dict[str, str]]:
        client = await self._client()
        response = await client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Return JSON with a questions array of prompt, skill, difficulty."},
                {"role": "user", "content": f"Generate {count} {role.value} interview practice questions."},
            ],
        )
        return json.loads(response.choices[0].message.content or "{}").get("questions", [])

    async def evaluate_answer(self, question: str, answer: str) -> dict[str, object]:
        client = await self._client()
        response = await client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "Return JSON: score 1-10, strengths array, weaknesses array, suggestions array.",
                },
                {"role": "user", "content": f"Question: {question}\nAnswer: {answer}"},
            ],
        )
        return json.loads(response.choices[0].message.content or "{}")


class GeminiService(MockAIService):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def _generate_json(self, prompt: str) -> dict[str, object]:
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        response = await model.generate_content_async(prompt)
        text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(text)

    async def generate_questions(self, role: InterviewRole, count: int) -> list[dict[str, str]]:
        data = await self._generate_json(
            f"Return JSON with questions array. Generate {count} {role.value} interview questions."
        )
        return data.get("questions", [])  # type: ignore[return-value]

    async def evaluate_answer(self, question: str, answer: str) -> dict[str, object]:
        return await self._generate_json(
            "Return JSON: score 1-10, strengths array, weaknesses array, suggestions array.\n"
            f"Question: {question}\nAnswer: {answer}"
        )
