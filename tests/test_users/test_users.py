import pytest

from django.core.exceptions import ValidationError

from apps.users.models import User
from apps.users.models.validators.user import validate_email

from tests.base import USER_LOGIN, USER_PASSWORD
from tests.test_users.factories import UserFactory


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


def test_validate_email(db):
    user = UserFactory.create(email='')

    validate_email(email='')

    user.email = 'test'
    user.save()

    with pytest.raises(ValidationError):
        validate_email(email='test')
