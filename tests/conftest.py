"""Pytest fixtures for isolated async API tests."""

import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_interview_platform.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-with-enough-length"
os.environ["AI_PROVIDER"] = "mock"

from app.database.base import Base
from app.database.session import get_db
from app.main import create_app
from app.models import Analytics, Answer, Evaluation, InterviewSession, Question, User

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine(TEST_DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    await engine.dispose()
