# app/celery.py

from celery import Celery
from kombu.serialization import register

# Ensure async support
celery_app = Celery(
    "aetherlms",
    broker="amqp://guest:guest@localhost:5672//",
    result_backend="rpc://",
    task_serializer="json",
    accept_content=["json"],
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)
# Autodiscover tasks in app modules (e.g., `tasks.py`)
celery_app.autodiscover_tasks(packages=["app.background_tasks"])

