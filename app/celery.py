from celery import Celery
from app.config import settings

# Load the Celery configuration from the environment variable or default to 'config.py'
# This should contain the configuration settings for Celery, including the broker URL.
celery_app = Celery(
    'app',  # The name of the Celery application
    broker=settings.CELERY_BROKER_URL,  # RabbitMQ URL or default broker
    backend=settings.CELERY_RESULT_BACKEND,  # The result backend to store task results
)

# Load configuration from a Python config file
celery_app.config_from_object('config')  # You can specify a configuration class for Celery

# Autodiscover tasks in all registered app modules (e.g., tasks.py)
celery_app.autodiscover_tasks(['app.background_tasks.tasks'])

# Optional: Print task-related logs to the console for debugging
celery_app.conf.update(
    task_track_started=True,  # Track tasks from start to finish
    worker_max_tasks_per_child=100,  # Max tasks a worker can process before restarting (helps with memory leaks)
    task_acks_late=True,  # Acknowledge the task after the worker has completed it (ensures reliability)
    task_reject_on_worker_lost=True,  # Reject tasks if the worker is lost
    task_time_limit=300,  # Max time for a task before it times out (in seconds)
)

# Optional: Configurations related to retries for failed tasks
celery_app.conf.update(
    task_default_retry_delay=10,  # Delay between retries for tasks (in seconds)
    task_default_max_retries=3,  # Max retry attempts for tasks
    task_retry_policy={
        'max_retries': 3,
        'interval_start': 1,  # Initial retry interval (in seconds)
        'interval_step': 2,  # Increment for subsequent retries
        'interval_max': 10,  # Max retry interval (in seconds)
    },
)

# Optional: Logging configurations (can be customized based on needs)
celery_app.conf.update(
    worker_log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    worker_task_log_format='%(asctime)s - %(task_name)s - %(levelname)s - %(message)s',
    loglevel='INFO',  # Choose the desired log level (DEBUG, INFO, WARNING, ERROR)
    enable_utc=True  # Set to True for UTC timestamps in logs
)

# Optional: Configure the retry behavior for task failure (based on task attributes)
celery_app.conf.update(
    task_acks_late=True,  # Delay acknowledgment until the task is finished
    task_reject_on_worker_lost=True,  # Reject task if the worker is lost
)

# Example of setting up periodic tasks (using Celery beat)
from datetime import timedelta

celery_app.conf.beat_schedule = {
    'send_assignment_reminders': {
        'task': 'app.background_tasks.tasks.send_assignment_reminders',
        'schedule': timedelta(hours=1),  # Run every hour
        'args': (),
    },
}

# Ensures that Celery starts up correctly and connects to the broker
if __name__ == '__main__':
    celery_app.start()
