import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

from celery import Celery
import os
from dotenv import load_dotenv
from loguru import logger
from kombu import Queue

# Load environment variables
load_dotenv()

# Get Redis URL from environment
# Railway provides REDIS_URL directly, or use CELERY_BROKER_URL, or construct from host/port
redis_url = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL")
if not redis_url:
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_url = f"redis://{redis_host}:{redis_port}/0"

# Create Celery instance
celery_app = Celery(
    "fintune_tasks",
    broker=redis_url,
    backend=redis_url,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_hijack_root_logger=False,
    task_routes={
        # Routes pour les tâches avec le préfixe app.tasks
        "app.tasks.content_processing.*": {"queue": "content_processing"},
        "app.tasks.dataset_generation.*": {"queue": "dataset_generation"},
        "app.tasks.fine_tuning.*": {"queue": "fine_tuning"},
        
        # Routes pour les tâches sans préfixe (utilisées dans les appels send_task)
        "generate_dataset": {"queue": "dataset_generation"},
        "process_pdf_content": {"queue": "content_processing"},
        "process_text_content": {"queue": "content_processing"},
        "process_youtube_content": {"queue": "content_processing"},
    },
)

# Ajouter cette configuration supplémentaire
celery_app.conf.broker_transport_options = {'visibility_timeout': 3600}  # 1 heure
celery_app.conf.broker_url = redis_url

# Import tasks to register them
from app.tasks import content_processing, dataset_generation, fine_tuning

# Example task for testing
@celery_app.task
def example_task(name):
    logger.info(f"Running example task for {name}")
    return f"Hello {name}!"

# Définir explicitement les queues
celery_app.conf.task_queues = (
    Queue('celery', routing_key='celery'),
    Queue('content_processing', routing_key='content_processing'),
    Queue('dataset_generation', routing_key='dataset_generation'),
    Queue('fine_tuning', routing_key='fine_tuning'),
)

if __name__ == "__main__":
    celery_app.start() 