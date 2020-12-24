import pytest

from apps.users.services.token import TokenService


@pytest.fixture()
def token_service():
    """Returns token service."""
    return TokenService()
