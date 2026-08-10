"""
Rate limiting via slowapi, backed by Redis (already running for
Celery/caching, so no new infrastructure). Limits are applied per-route,
not globally - auth endpoints get tight limits (brute-force protection),
AI-calling endpoints get moderate limits (cost/abuse protection), and
most CRUD endpoints are left unlimited since the NFR target is <300ms
on cheap operations, not throttling normal usage.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)