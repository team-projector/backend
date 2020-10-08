from apps.users.services.user.gl.manager import UserGlManager
from tests.test_users.factories.gitlab import GlUserFactory


def test_success(user):
    """
    Test success.

    :param user:
    """
    gl_user = GlUserFactory.create(id=user.gl_id)

    assert UserGlManager().extract_user_from_data(gl_user) == user


def test_empty_data(user):
    """
    Test empty data.

    :param user:
    """
    assert UserGlManager().extract_user_from_data({}) is None
