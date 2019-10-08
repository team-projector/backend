# -*- coding: utf-8 -*-

from actstream import action

from apps.users.models import User
from celery_app import app


@app.task
def add_action(**kwargs) -> None:
    """Add action."""
    action.send(kwargs.pop('sender_id', User.objects.system_user), **kwargs)
