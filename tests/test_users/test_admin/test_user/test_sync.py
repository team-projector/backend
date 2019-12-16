# -*- coding: utf-8 -*-

from django.test import override_settings

from tests.test_users.factories.gitlab import GlUserFactory
from tests.test_users.factories.user import UserFactory
from tests.test_users.helpers.gitlab_checkers import check_user


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_handler(user_admin, db, gl_mocker):
    """Test user sync from admin."""
    gl_user = GlUserFactory()

    user = UserFactory.create(gl_id=gl_user['id'])
    gl_mocker.registry_get('/users/{0}'.format(gl_user['id']), gl_user)

    user_admin.sync_handler(user)

    user.refresh_from_db()
    check_user(user, gl_user)
