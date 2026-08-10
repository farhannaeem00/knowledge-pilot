"""
Aggregates all v1 route modules.
"""
from fastapi import APIRouter

from app.presentation.api.v1 import (
    admin,
    auth,
    chat,
    collections,
    folders,
    health,
    highlights,
    notes,
    notifications,
    scripts,
    search,
    summaries,
    workspaces,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(workspaces.router)
api_router.include_router(summaries.router)
api_router.include_router(chat.router)
api_router.include_router(notes.router)
api_router.include_router(highlights.router)
api_router.include_router(search.router)
api_router.include_router(scripts.router)
api_router.include_router(folders.router)
api_router.include_router(collections.router)
api_router.include_router(notifications.router)
api_router.include_router(admin.router)