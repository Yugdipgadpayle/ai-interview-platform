"""Interview workflow tests."""

import pytest
from httpx import AsyncClient


async def auth_headers(client: AsyncClient) -> dict[str, str]:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "candidate@example.com", "full_name": "Candidate", "password": "strongpass123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "candidate@example.com", "password": "strongpass123"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.mark.asyncio
async def test_interview_answer_analytics_and_report(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    created = await client.post(
        "/api/v1/interviews",
        json={"role": "backend", "question_count": 2},
        headers=headers,
    )
    assert created.status_code == 201
    session = created.json()
    assert len(session["questions"]) == 2

    question_id = session["questions"][0]["id"]
    answer = await client.post(
        f"/api/v1/interviews/questions/{question_id}/answers",
        json={"content": "I would design the API with clear contracts, rate limits, retries, metrics, and tests."},
        headers=headers,
    )
    assert answer.status_code == 201
    assert 1 <= answer.json()["evaluation"]["score"] <= 10

    analytics = await client.get("/api/v1/analytics/summary", headers=headers)
    assert analytics.status_code == 200
    assert analytics.json()["total_interviews"] == 1
    assert analytics.json()["average_score"] > 0

    report = await client.get("/api/v1/reports/interview.pdf", headers=headers)
    assert report.status_code == 200
    assert report.headers["content-type"] == "application/pdf"
