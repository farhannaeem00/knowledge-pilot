"""
Liveness (`/health`) and readiness (`/ready`) endpoints.
"""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.infrastructure.db.session import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict:
    return {"status": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def ready() -> JSONResponse:
    db_ok = await check_db_connection()
    if not db_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "database": "unreachable"},
        )
    return JSONResponse(content={"status": "ready", "database": "ok"})