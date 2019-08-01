from django.test import override_settings

from apps.users.models import User
from tests.base import model_admin
from tests.test_users.factories import UserFactory
from tests.test_development.factories_gitlab import AttrDict, GlUserFactory
from tests.test_development.checkers_gitlab import check_user


def test_change_password_link(admin_user):
    ma_user = model_admin(User)

    assert ma_user.change_password_link(admin_user) == \
           f'<a href="/admin/users/user/{admin_user.id}/password/">' \
           f'change password</a>'


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


def test_changelist_view_without_referer(admin_client):
    ma_user = model_admin(User)

    request = admin_client.get('/admin/users/user/')

    assert request.META['QUERY_STRING'] == ''

    ma_user.changelist_view(request)

    assert request.META['QUERY_STRING'] == 'is_active__exact=1'


def test_changelist_view_with_referer(admin_client):
    ma_user = model_admin(User)

    url = '/admin/users/user/'
    request_1 = admin_client.get(url, HTTP_REFERER=url)
    request_2 = admin_client.get(url, HTTP_REFERER='www.test.com')

    assert request_1.META['QUERY_STRING'] == ''

    ma_user.changelist_view(request_1)

    assert request_1.META['QUERY_STRING'] == ''

    ma_user.changelist_view(request_2)

    assert request_2.META['QUERY_STRING'] == 'is_active__exact=1'


def test_user_instance_str(db):
    user = UserFactory.create(login='test_login')

    assert str(user) == 'test_login'
    assert user.get_short_name() == 'test_login'