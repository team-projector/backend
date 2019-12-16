import pytest
from django.core.exceptions import ValidationError

from apps.users.models.validators.user import validate_email
from tests.test_users.factories.user import UserFactory


def test_empty_email(db):
    """Test empty email."""
    validate_email(email='')


def test_non_unique_email(db):
    """Test if email already used."""
    UserFactory.create(email='user@mail.com')

    with pytest.raises(ValidationError):
        validate_email(email='user@mail.com')
