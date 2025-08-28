import os
import ssl
from celery import Celery

# Make sure Django settings are loaded before Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("backend")

app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    broker_use_ssl={
        "ssl_cert_reqs": ssl.CERT_NONE   # use CERT_REQUIRED if you add certs
    } if redis_url.startswith("rediss://") else None,
    redis_backend_use_ssl={
        "ssl_cert_reqs": ssl.CERT_NONE
    } if redis_url.startswith("rediss://") else None,
)

# Load Django settings with CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in your apps
app.autodiscover_tasks()
