"""
Auth use cases - orchestrate repositories + security helpers.
No FastAPI or SQLAlchemy imports here; this layer only knows about the
repository interfaces and domain-meaningful exceptions.
"""
from datetime import datetime, UTC

from app.application.interfaces.repositories import (
    RefreshTokenRepositoryInterface,
    UserRepositoryInterface,
)
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.infrastructure.db.models.user import User


class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

    async def execute(self, *, email: str, password: str, full_name: str | None) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictError("An account with this email already exists")
        return await self.user_repo.create(
            email=email, password_hash=hash_password(password), full_name=full_name
        )


class LoginUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryInterface,
        refresh_token_repo: RefreshTokenRepositoryInterface,
    ):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo

    async def execute(self, *, email: str, password: str) -> tuple[User, str, str]:
        """Returns (user, access_token, raw_refresh_token)."""
        user = await self.user_repo.get_by_email(email)
        if not user or not user.password_hash or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")

        access_token = create_access_token(str(user.id))
        raw_refresh, refresh_hash, expires_at = generate_refresh_token()
        await self.refresh_token_repo.create(
            user_id=user.id, token_hash=refresh_hash, expires_at=expires_at
        )
        return user, access_token, raw_refresh


class RefreshTokenUseCase:
    def __init__(self, refresh_token_repo: RefreshTokenRepositoryInterface):
        self.refresh_token_repo = refresh_token_repo

    async def execute(self, *, raw_refresh_token: str) -> tuple[str, str]:
        """Returns (new_access_token, new_raw_refresh_token). Rotates on every use."""
        token_hash = hash_refresh_token(raw_refresh_token)
        existing = await self.refresh_token_repo.get_by_hash(token_hash)

        if not existing or existing.revoked_at is not None:
            raise UnauthorizedError("Invalid or revoked refresh token")
        if existing.expires_at < datetime.now(UTC):
            raise UnauthorizedError("Refresh token expired")

        await self.refresh_token_repo.revoke(existing)

        new_access_token = create_access_token(str(existing.user_id))
        new_raw_refresh, new_hash, new_expires_at = generate_refresh_token()
        await self.refresh_token_repo.create(
            user_id=existing.user_id, token_hash=new_hash, expires_at=new_expires_at
        )
        return new_access_token, new_raw_refresh


class LogoutUseCase:
    def __init__(self, refresh_token_repo: RefreshTokenRepositoryInterface):
        self.refresh_token_repo = refresh_token_repo

    async def execute(self, *, raw_refresh_token: str) -> None:
        token_hash = hash_refresh_token(raw_refresh_token)
        existing = await self.refresh_token_repo.get_by_hash(token_hash)
        if existing and existing.revoked_at is None:
            await self.refresh_token_repo.revoke(existing)
