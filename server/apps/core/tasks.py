from actstream import action

from apps.users.models import User
from celery_app import app


@app.task
def add_action(**kwargs) -> None:
    # TODO: need default sender
    sender_id = kwargs.pop('sender_id', None)
    sender = User.objects.get(id=sender_id) if sender_id else User.objects.order_by('id').first()

    action.send(sender, **kwargs)
