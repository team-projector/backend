import pytest
from django.core.exceptions import ValidationError
from tests.fixtures.users import DEFAULT_USER_PASSWORD, DEFAULT_USERNAME
from tests.test_users.factories.user import UserFactory

from apps.users.models import User
from apps.users.models.validators.user import validate_email


def test_create_user(db):
    User.objects.create_user(DEFAULT_USERNAME)

    user = User.objects.first()

    assert user.login == DEFAULT_USERNAME


def test_create_user_without_login(db):
    with pytest.raises(TypeError):
        User.objects.create_user()

    with pytest.raises(ValueError):
        User.objects.create_user(login=None)


def test_create_superuser(db):
    User.objects.create_superuser(DEFAULT_USERNAME, DEFAULT_USER_PASSWORD)

    user = User.objects.first()

    assert user.login == DEFAULT_USERNAME
    assert user.is_superuser is True


def test_validate_email(db):
    user = UserFactory.create(email='')

    validate_email(email='')

    user.email = 'test'
    user.save()

    with pytest.raises(ValidationError):
        validate_email(email='test')
