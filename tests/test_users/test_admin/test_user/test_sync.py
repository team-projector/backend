# -*- coding: utf-8 -*-

from django.test import override_settings

from apps.users.models import User
from tests.helpers.base import model_admin
from tests.test_development.checkers_gitlab import check_user
from tests.test_development.factories_gitlab import AttrDict, GlUserFactory
from tests.test_users.factories.user import UserFactory


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_handler(db, gl_mocker):
    ma_user = model_admin(User)

    gl_mocker.registry_get('/user', GlUserFactory())

    gl_user = AttrDict(GlUserFactory())
    user = UserFactory.create(gl_id=gl_user.id)
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    ma_user.sync_handler(user)

    user.refresh_from_db()
    check_user(user, gl_user)
