"""
Celery application instance. The worker process runs this via:
    celery -A app.infrastructure.celery_app worker --loglevel=info
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "knowledgepilot",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.infrastructure.tasks.document_processing_tasks",
        "app.infrastructure.tasks.summary_tasks",
        "app.infrastructure.tasks.script_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
