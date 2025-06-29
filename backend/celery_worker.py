from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)