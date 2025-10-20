"""Celery application setup for Content Factory."""
from celery import Celery
from config import Config

celery_app = Celery(
    'content_factory',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=['tasks.trends']
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_expires=3600,
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True
)

# Ensure task modules are imported so Celery registers them
try:  # pragma: no cover - import side effects only
    import tasks.trends  # noqa: F401
except Exception:
    pass
