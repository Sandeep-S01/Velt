"""
Celery configuration and application entry point.
"""

import os
import sys
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "smartsearch_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Celery Configurations
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=1500,
    task_time_limit=1800,
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "sync-due-shopify-stores": {
            "task": "app.tasks.sync.sync_due_shopify_stores_task",
            "schedule": 900.0,
        },
    },
)

# Enable eager execution during testing
if "pytest" in sys.modules or os.getenv("TESTING") == "true":
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
