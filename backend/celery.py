import os
from celery import Celery
import ssl

redis_url = os.getenv("REDIS_URL")
app = Celery('backend')

app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE
        } if redis_url.startswith('rediss://') else None
)

redis_backend_use_ssl={
    'ssl_cert_reqs': ssl.CERT_NONE
    } if redis_url.startswith('rediss://') else None

os.environ.setdefault('DJANGO_SETTINGS_MODULE','backend.settings')


app.config_from_object('django.conf:settings',namespace='CELERY')
app.autodiscover_tasks()

