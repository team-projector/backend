import pytest

from apps.users.models import User
from apps.users.services.user.system import (
    SYSTEM_USERNAME,
    create_system_user,
    get_system_user,
)


def test_exists(db):
    """Test if exists."""
    create_system_user()

    user = get_system_user()
    assert user is not None
    assert user.login == SYSTEM_USERNAME


def test_not_exists(db):
    """Test if not exists."""
    with pytest.raises(User.DoesNotExist):
        get_system_user()
