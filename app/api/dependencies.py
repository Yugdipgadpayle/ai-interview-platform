"""FastAPI dependency providers for repositories, services, and authorization."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.database.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.interview_repository import InterviewRepository
from app.repositories.user_repository import UserRepository
from app.services.ai_service import AIService, GeminiService, MockAIService, OpenAIService
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService
from app.services.cache_service import CacheService
from app.services.interview_service import InterviewService
from app.services.report_service import ReportService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_interview_repository(db: AsyncSession = Depends(get_db)) -> InterviewRepository:
    return InterviewRepository(db)


async def get_auth_service(users: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(users)


async def get_ai_service() -> AIService:
    settings = get_settings()
    if settings.ai_provider == "openai" and settings.openai_api_key:
        return OpenAIService(settings.openai_api_key, settings.openai_model)
    if settings.ai_provider == "gemini" and settings.gemini_api_key:
        return GeminiService(settings.gemini_api_key, settings.gemini_model)
    return MockAIService()


async def get_interview_service(
    interviews: InterviewRepository = Depends(get_interview_repository),
    ai: AIService = Depends(get_ai_service),
) -> InterviewService:
    return InterviewService(interviews, ai)


async def get_analytics_service(
    interviews: InterviewRepository = Depends(get_interview_repository),
) -> AnalyticsService:
    return AnalyticsService(interviews)


async def get_report_service() -> ReportService:
    return ReportService()


async def get_cache_service() -> AsyncGenerator[CacheService, None]:
    cache = CacheService()
    try:
        yield cache
    finally:
        await cache.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    users: UserRepository = Depends(get_user_repository),
) -> User:
    try:
        user_id = int(decode_token(token, "access"))
    except ValueError as exc:
        raise UnauthorizedError("Invalid access token") from exc
    user = await users.get_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("Inactive or missing user")
    return user


def require_role(*roles: UserRole):
    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ForbiddenError("Insufficient permissions")
        return user

    return checker
