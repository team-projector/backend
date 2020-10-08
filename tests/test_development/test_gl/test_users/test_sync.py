from apps.users.models import User
from apps.users.services.user.gl.manager import UserGlManager
from tests.test_development.test_gl.helpers import gl_checkers, gl_mock
from tests.test_users.factories.gitlab import GlUserFactory
from tests.test_users.factories.user import UserFactory


def test_success(db, gl_mocker):
    """
    Test success.

    :param db:
    :param gl_mocker:
    """
    gl_user = GlUserFactory.create()

    gl_mock.register_user(gl_mocker, gl_user)

    UserGlManager().sync_user(gl_user["id"])

    user = User.objects.get(login=gl_user["username"])

    gl_checkers.check_user(user, gl_user)


def test_already_exists_email_filled(db, gl_mocker):
    """
    Test already exists email filled.

    :param db:
    :param gl_mocker:
    """
    gl_user = GlUserFactory.create(public_email="gitlab_email")

    user = UserFactory.create(gl_id=gl_user["id"], email="db_email")

    gl_mock.register_user(gl_mocker, gl_user)

    UserGlManager().sync_user(gl_user["id"])

    user.refresh_from_db()

    assert user.login == gl_user["username"]
    assert user.email == "db_email"


def test_already_exists_email_empty(db, gl_mocker):
    """
    Test already exists email empty.

    :param db:
    :param gl_mocker:
    """
    gl_user = GlUserFactory.create(public_email="gitlab_email")

    user = UserFactory.create(gl_id=gl_user["id"], email="")

    gl_mock.register_user(gl_mocker, gl_user)

    UserGlManager().sync_user(gl_user["id"])

    user.refresh_from_db()

    assert user.login == gl_user["username"]
    assert user.email == "gitlab_email"


def test_update_users(db, gl_mocker):
    """
    Test update users.

    :param db:
    :param gl_mocker:
    """
    gl_user = GlUserFactory.create(name="new name")
    UserFactory.create(gl_id=gl_user["id"], name="old name")

    UserFactory.create_batch(3)

    gl_mock.register_user(gl_mocker, gl_user)

    UserGlManager().sync_users()

    user = User.objects.get(gl_id=gl_user["id"])

    gl_checkers.check_user(user, gl_user)
