from celery.beat import crontab

class CeleryConfig:
    # Use RabbitMQ as the message broker
    broker_url = "amqp://guest:guest@localhost:5672//"

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
    # beat_schedule = {
    #     'clean-submissions-weekly': {
    #         'task': 'app.background_tasks.tasks.clean_old_submissions_task',
    #         'schedule': crontab(day_of_week='sunday', hour=4)
    #     },
    # }


celery_config = CeleryConfig()

