from django.test import override_settings

from apps.development.services.gitlab.users import load_user, update_users
from apps.users.models import User

from tests.test_development.factories_gitlab import AttrDict, GlUserFactory
from tests.test_users.factories import UserFactory


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_user(db, gl_mocker):
    gl_user = AttrDict(GlUserFactory())

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    load_user(gl_user.id)

    user = User.objects.get(login=gl_user.username)

    _check_user(user, gl_user)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_update_users(db, gl_mocker):
    gl_user = AttrDict(GlUserFactory(name='new name'))
    UserFactory.create(gl_id=gl_user.id, name='old name')

    UserFactory.create_batch(3)

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    update_users()

    user = User.objects.get(gl_id=gl_user.id)

    _check_user(user, gl_user)


def _check_user(user, gl_user):
    assert user.login == gl_user.username
    assert user.name == gl_user.name
    assert user.gl_avatar == gl_user.avatar_url
    assert user.gl_url == gl_user.web_url
