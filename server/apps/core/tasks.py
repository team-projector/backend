from actstream import action

from apps.users.models import User
from celery_app import app


@app.task(queue='low_priority')
def add_action(sender, **kwargs) -> None:
    # TODO: need default sender
    sender = sender or User.objects.filter(is_superuser=True).order_by('id').first()

    action.send(sender, **kwargs)
