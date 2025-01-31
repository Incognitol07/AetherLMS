# app/celery.py

from celery import Celery
from app.celery_config import celery_config

celery_app = Celery("app")

# Load configuration from our Celery config class
celery_app.config_from_object(celery_config)

# Autodiscover tasks in app modules (e.g., `tasks.py`)
celery_app.autodiscover_tasks(["app.background_tasks.tasks"])

