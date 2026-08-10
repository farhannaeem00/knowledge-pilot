"""
Structured (JSON) logging so log aggregators can query fields like
`level`, `logger`, and `request_id` without a later migration.
"""
import logging
import sys
from datetime import datetime, timezone

from pythonjsonlogger import jsonlogger

from app.core.config import settings


class _UTCFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["app"] = settings.APP_NAME
        log_record["env"] = settings.APP_ENV


def configure_logging() -> None:
    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_UTCFormatter("%(timestamp)s %(level)s %(logger)s %(message)s"))
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    for noisy in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING if not settings.DEBUG else logging.INFO)
