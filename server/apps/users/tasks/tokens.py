# -*- coding: utf-8 -*-

from apps.users.services.token import clear_tokens
from celery_app import app


@app.task
def clear_expired_tokens_task() -> None:
    """Clears expired tokens."""
    clear_tokens()
