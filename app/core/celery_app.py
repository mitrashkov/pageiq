import os
import sys

from celery import Celery

from app.core.config import settings


def _running_under_pytest() -> bool:
    # `PYTEST_CURRENT_TEST` is set only while tests execute; also detect import-time.
    if "pytest" in sys.modules:
        return True
    return bool(os.getenv("PYTEST_CURRENT_TEST"))


celery_app = Celery(
    "pageiq",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# In unit tests we want deterministic, in-process tasks.
celery_app.conf.task_always_eager = _running_under_pytest()
celery_app.conf.task_eager_propagates = True

# Reasonable defaults
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

