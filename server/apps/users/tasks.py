from celery_app import app
from .services.token import clear_tokens


# TODO: should rename
@app.task
def clear_expired_tokens() -> None:
    clear_tokens()
