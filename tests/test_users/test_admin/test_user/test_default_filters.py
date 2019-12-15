# -*- coding: utf-8 -*-

from http import HTTPStatus

import pytest


def test_no_referer(user_admin, admin_client):
    """Test apply if no referer."""
    request = admin_client.get('/admin/users/user/')
    response = user_admin.changelist_view(request)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == '/admin/users/user/?is_active__exact=1'


@pytest.mark.parametrize('referer', [
    'www.test.com',
    '/admin/',
    None
])
def test_apply_by_referer(user_admin, admin_client, referer):
    """Test apply if suitable referer."""
    request = admin_client.get(
        '/admin/users/user/',
        HTTP_REFERER=referer,
    )

    response = user_admin.changelist_view(request)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == '/admin/users/user/?is_active__exact=1'


def test_referer_same_url(user_admin, admin_client):
    """Test no apply if same referer."""
    request = admin_client.get(
        '/admin/users/user/',
        HTTP_REFERER='/admin/users/user/',
    )

    response = user_admin.changelist_view(request)

    assert response.status_code == HTTPStatus.OK
