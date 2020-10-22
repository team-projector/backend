from actstream import action
from django.contrib.auth import get_user_model

from celery_app import app

User = get_user_model()


@app.task
def add_action_task(**kwargs) -> None:
    """Add action."""
    action.send(
        kwargs.pop("sender_id", User.objects.system_user),
        **kwargs,
    )
