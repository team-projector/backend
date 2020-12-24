from apps.core import injector
from apps.users.services.token import TokenService
from celery_app import app


@app.task
def clear_expired_tokens_task() -> None:
    """Clears expired tokens."""
    token_service = injector.get(TokenService)
    token_service.clear_tokens()
