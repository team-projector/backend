# -*- coding: utf-8 -*-

from apps.users.services.user.gl.manager import UserGlManager
from celery_app import app


@app.task
def sync_user_task(gl_id: int) -> None:
    """Syncing user from Gitlab."""
    UserGlManager().sync_user(gl_id)
