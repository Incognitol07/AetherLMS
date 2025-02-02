# app/background_tasks/jobs/system_jobs.py
from app.models import Submission
from app.database import SessionLocal
from datetime import datetime, timedelta, timezone

# TODO: Change to async completely
# TODO: send a notification to users for deleted submissions
# TODO: add more system jobs
async def clean_old_submissions(days=365):
    async with SessionLocal() as db:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        old_submissions = (
            db.query(Submission).filter(Submission.submitted_at < cutoff).delete()
        )
        db.commit()


async def perform_database_backup():
    # Implementation for database backup
    pass

