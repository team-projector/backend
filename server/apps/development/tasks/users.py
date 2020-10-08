from apps.core.exceptions import sync_exceptions
from apps.users.services.user.gl.manager import UserGlManager
from celery_app import app


@app.task(throws=sync_exceptions)
def sync_user_task(gl_id: int) -> None:
    """Syncing user from Gitlab."""
    UserGlManager().sync_user(gl_id)
