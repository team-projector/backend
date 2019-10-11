# -*- coding: utf-8 -*-

from apps.users.services.user.gitlab import load_user
from celery_app import app


@app.task
def sync_user(gl_id: int) -> None:
    """Syncing user from Gitlab."""
    load_user(gl_id)
