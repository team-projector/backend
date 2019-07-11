from celery_app import app
from .services.token import clear_tokens


@app.task
def clear_expired_tokens() -> None:
    clear_tokens()
