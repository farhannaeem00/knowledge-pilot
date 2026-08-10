"""
Synchronous SQLAlchemy engine/session, used only by Celery tasks.

Celery workers run outside FastAPI's async event loop, so reusing the
async engine from session.py would fight the framework. A plain sync
session for the worker is the standard, low-risk pattern here.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Same database, different driver: asyncpg (async, for FastAPI) vs
# psycopg2 (sync, for Celery). Same DATABASE_URL, just swap the dialect.
_sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

sync_engine = create_engine(_sync_url, pool_pre_ping=True, future=True)

SyncSessionLocal = sessionmaker(bind=sync_engine, autoflush=False, expire_on_commit=False)
