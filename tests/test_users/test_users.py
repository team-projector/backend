import pytest

from apps.users.models import User

from tests.base import USER_LOGIN, USER_PASSWORD


def test_create_user(db):
    User.objects.create_user(USER_LOGIN)

    user = User.objects.first()

    assert user.login == USER_LOGIN


def test_create_user_without_login(db):
    with pytest.raises(TypeError):
        User.objects.create_user()

    with pytest.raises(ValueError):
        User.objects.create_user(login=None)


def test_create_superuser(db):
    User.objects.create_superuser(USER_LOGIN, USER_PASSWORD)

    user = User.objects.first()

    assert user.login == USER_LOGIN
    assert user.is_superuser is True
