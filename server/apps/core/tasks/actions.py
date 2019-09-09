from actstream import action

from apps.users.models import User
from celery_app import app


@app.task
def add_action(**kwargs) -> None:
    action.send(kwargs.pop('sender_id', User.objects.system_user), **kwargs)