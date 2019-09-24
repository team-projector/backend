# -*- coding: utf-8 -*-

from celery_app import app
from ..services.gitlab.users import load_user


@app.task
def sync_user(gl_id: int) -> None:
    load_user(gl_id)
