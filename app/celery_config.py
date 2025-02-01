from datetime import timedelta

class CeleryConfig:
    # Use RabbitMQ as the message broker
    broker_url = "pyamqp://guest:guest@localhost//"

    # Use a database or RPC as a result backend (RabbitMQ doesn't support result storage natively)
    result_backend = "rpc://"

    # Task settings
    task_track_started = True
    task_acks_late = True
    task_reject_on_worker_lost = True
    task_time_limit = 300

    # Retry settings
    task_default_retry_delay = 10
    task_default_max_retries = 3
    task_retry_policy = {
        "max_retries": 3,
        "interval_start": 1,
        "interval_step": 2,
        "interval_max": 10,
    }

    # Logging configurations
    worker_log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    worker_task_log_format = "%(asctime)s - %(task_name)s - %(levelname)s - %(message)s"
    task_serializer = "json"
    accept_content = ["json"]

    # Celery Beat configuration for periodic tasks
    # beat_schedule = {
    #     "send_assignment_reminders": {
    #         "task": "app.background_tasks.jobs.send_assignment_reminders",
    #         "schedule": timedelta(hours=1),
    #         "args": (),
    #     },
    # }


celery_config = CeleryConfig()

