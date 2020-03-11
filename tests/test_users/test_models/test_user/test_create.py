import pytest
from django.utils.translation import gettext as _

from apps.users.models import User
from tests.fixtures.users import DEFAULT_USER_PASSWORD, DEFAULT_USERNAME


def test_normal_user(db):
    """Test creation normal user."""
    User.objects.create_user(DEFAULT_USERNAME)

    assert User.objects.filter(login=DEFAULT_USERNAME).exists()


def test_superuser(db):
    """Test creation super user."""
    User.objects.create_superuser(
        DEFAULT_USERNAME,
        DEFAULT_USER_PASSWORD,
    )

    assert User.objects.filter(
        login=DEFAULT_USERNAME,
        is_superuser=True,
    ).exists()


def test_with_login_none(db):
    """Test if login None."""
    with pytest.raises(ValueError, match=_("VN__USER_MUST_HAVE_A_LOGIN")):
        User.objects.create_user(login=None)
