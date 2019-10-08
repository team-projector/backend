# -*- coding: utf-8 -*-

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

app = Celery('server')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(worker_pool_restarts=True)
app.conf.timezone = 'UTC'

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """Add periodic tasks."""
    from apps.development.tasks import sync
    from apps.users.tasks import clear_expired_tokens

    sender.add_periodic_task(
        60 * 60,
        sync.s(),
        name='gitlab sync',
    )

    sender.add_periodic_task(
        crontab(minute=0, hour=0),
        clear_expired_tokens.s(),
        name='clear expired tokens',
    )
