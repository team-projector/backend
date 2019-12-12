from django.test import override_settings
from tests.test_development.checkers_gitlab import check_user
from tests.test_development.factories_gitlab import AttrDict, GlUserFactory

from apps.development.tasks import sync_user_task
from apps.users.models import User


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_user_task(db, gl_mocker):
    gl_user = AttrDict(GlUserFactory())

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    sync_user_task(gl_user.id)

    user = User.objects.get(gl_id=gl_user.id)

    check_user(user, gl_user)
