from django.test import override_settings

from apps.development.services.gitlab.users import (
    extract_user_from_data,
    load_user,
    update_users,
)
from apps.users.models import User

from tests.test_development.checkers_gitlab import check_user
from tests.test_development.factories_gitlab import AttrDict, GlUserFactory
from tests.test_users.factories import UserFactory


def test_extract_user_from_data(user):
    assert extract_user_from_data({}) is None

    gl_user = AttrDict(GlUserFactory(id=user.gl_id))

    assert extract_user_from_data(gl_user) == user


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_user(db, gl_mocker):
    gl_user = AttrDict(GlUserFactory())

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    load_user(gl_user.id)

    user = User.objects.get(login=gl_user.username)

    check_user(user, gl_user)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_user_without_gl_email(db, gl_mocker):
    gl_user = AttrDict(GlUserFactory())

    user = UserFactory.create(gl_id=gl_user.id, email='email_exists')

    gl_mocker.registry_get('/user', GlUserFactory(public_email='gitlab_email'))
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    load_user(gl_user.id)

    user.refresh_from_db()

    assert user.login == gl_user.username
    assert user.email == 'email_exists'


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_update_users(db, gl_mocker):
    gl_user = AttrDict(GlUserFactory(name='new name'))
    UserFactory.create(gl_id=gl_user.id, name='old name')

    UserFactory.create_batch(3)

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    update_users()

    user = User.objects.get(gl_id=gl_user.id)

    check_user(user, gl_user)
