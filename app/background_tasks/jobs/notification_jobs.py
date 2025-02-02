# app/background_tasks/jobs/notification_jobs.py
from app.models import Notification, User, BackgroundTask, Assignment
from app.database import SessionLocal
from datetime import datetime, timedelta


# TODO: generate effective async and necessary background jobs for notifications