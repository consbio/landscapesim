import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'landscapesim_project.settings')

from django.conf import settings  # noqa

app = Celery('landscapesim_project')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.CELERYBEAT_SCHEDULE = settings.CELERYBEAT_SCHEDULE
