"""
Pytest fixtures for a real (not mocked) test database. Uses a separate
Postgres database (knowledgepilot_test) so tests never touch dev data,
with tables created fresh and dropped after each test module - genuine
integration tests, not mocks, matching how this whole project has been
verified so far (real Docker, real Postgres, real Groq calls).
"""
import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.infrastructure.db.base import Base
from app.infrastructure.db.models import *  # noqa: F401,F403 registers all models
from app.infrastructure.db.session import get_db
from app.main import app

TEST_DATABASE_URL = settings.DATABASE_URL.rsplit("/", 1)[0] + "/knowledgepilot_test"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    from sqlalchemy import text

    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_engine):
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()



@pytest_asyncio.fixture(autouse=True)
async def reset_rate_limiter():
    """
    Rate limiting (Step 14) is real and Redis-backed - correct in
    production, but multiple tests hitting /auth/register rapidly from
    the same test-runner IP would otherwise trip it. Reset before every
    test so rate-limit state never leaks between tests.
    """
    from app.infrastructure.rate_limiting.limiter import limiter

    limiter.reset()
    yield