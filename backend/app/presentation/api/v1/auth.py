"""
Auth endpoints: register, login, refresh, logout, me.
"""
from fastapi import APIRouter, Depends, status

from app.application.use_cases.auth_use_cases import (
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
)
from app.infrastructure.db.models.user import User
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.presentation.api.v1.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.presentation.api.v1.schemas.user import UserOut
from app.presentation.dependencies import (
    get_current_user,
    get_refresh_token_repository,
    get_user_repository,
)
from fastapi import Request

from app.infrastructure.rate_limiting.limiter import limiter
from app.infrastructure.repositories.audit_log_repository import AuditLogRepository
from app.presentation.dependencies import get_audit_log_repository
router = APIRouter(prefix="/auth", tags=["auth"])
from app.presentation.api.v1.schemas.user import UserUpdate 


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    payload: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository),
    audit_repo: AuditLogRepository = Depends(get_audit_log_repository),
) -> UserOut:
    use_case = RegisterUserUseCase(user_repo)
    user = await use_case.execute(
        email=payload.email, password=payload.password, full_name=payload.full_name
    )
    await audit_repo.log(
        user_id=user.id, action="user_registered", entity_type="user", entity_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository),
    refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
    audit_repo: AuditLogRepository = Depends(get_audit_log_repository),
) -> TokenResponse:
    use_case = LoginUseCase(user_repo, refresh_token_repo)
    user, access_token, raw_refresh = await use_case.execute(
        email=payload.email, password=payload.password
    )
    await audit_repo.log(
        user_id=user.id, action="user_login", entity_type="user", entity_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    )
    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> TokenResponse:
    use_case = RefreshTokenUseCase(refresh_token_repo)
    access_token, raw_refresh = await use_case.execute(raw_refresh_token=payload.refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: RefreshRequest,
    refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> None:
    use_case = LogoutUseCase(refresh_token_repo)
    await use_case.execute(raw_refresh_token=payload.refresh_token)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
@router.patch("/me", response_model=UserOut)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserOut:
    updated = await user_repo.update(
        current_user, full_name=payload.full_name, avatar_url=payload.avatar_url, bio=payload.bio
    )
    return UserOut.model_validate(updated)
