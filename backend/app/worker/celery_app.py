from celery import Celery
from app.core.config import settings

celery = Celery(
    "worker",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

celery.conf.task_routes = {
    "app.worker.test_task": "main-queue",
}

@celery.task(name="test_task")
def test_task(word: str) -> str:
    return f"test task return {word}"
