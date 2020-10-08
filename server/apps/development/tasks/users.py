from requests.exceptions import ReadTimeout

from apps.users.services.user.gl.manager import UserGlManager
from celery_app import app


@app.task(throws=(ReadTimeout,))
def sync_user_task(gl_id: int) -> None:
    """Syncing user from Gitlab."""
    UserGlManager().sync_user(gl_id)
