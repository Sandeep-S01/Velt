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
)

# Enable eager execution during testing
if "pytest" in sys.modules or os.getenv("TESTING") == "true":
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
