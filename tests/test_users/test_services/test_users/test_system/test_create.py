from apps.users.models import User
from apps.users.services.user.system import SYSTEM_USERNAME, create_system_user


def test_create(db):
    """Test user creation."""
    assert not User.objects.filter(login=SYSTEM_USERNAME).exists()

    create_system_user()
    user = User.objects.filter(login=SYSTEM_USERNAME).first()
    assert user is not None
    assert not user.is_active
    assert not user.is_superuser
    assert not user.is_staff


def test_exists(db):
    """Test if already presented."""
    create_system_user()
    assert User.objects.filter(login=SYSTEM_USERNAME).exists()

    create_system_user()
    assert User.objects.count() == 1
