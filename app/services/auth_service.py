"""Business logic for registration, login, and token refresh."""

from datetime import timedelta

from app.core.config import get_settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPair, UserCreate, UserLogin


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def register(self, payload: UserCreate) -> User:
        existing = await self.users.get_by_email(payload.email)
        if existing:
            raise ConflictError("Email is already registered")
        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )
        return await self.users.create(user)

    async def login(self, payload: UserLogin) -> TokenPair:
        user = await self.users.get_by_email(payload.email)
        if not user or not user.is_active or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        return self._token_pair(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        user_id = decode_token(refresh_token, "refresh")
        user = await self.users.get_by_id(int(user_id))
        if not user or not user.is_active:
            raise UnauthorizedError("Invalid refresh token")
        return self._token_pair(user)

    def _token_pair(self, user: User) -> TokenPair:
        settings = get_settings()
        return TokenPair(
            access_token=create_token(
                str(user.id), "access", timedelta(minutes=settings.access_token_expire_minutes)
            ),
            refresh_token=create_token(
                str(user.id), "refresh", timedelta(minutes=settings.refresh_token_expire_minutes)
            ),
        )
