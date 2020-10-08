from http import HTTPStatus

import pytest


def test_no_referer(user_admin, admin_rf):
    """Test apply if no referer."""
    response = user_admin.changelist_view(admin_rf.get("/admin/users/user/"))

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == "/admin/users/user/?is_active__exact=1"


@pytest.mark.parametrize("referer", ["www.test.com", "/admin/", None])
def test_apply_by_referer(user_admin, admin_rf, referer):
    """Test apply if suitable referer."""
    response = user_admin.changelist_view(
        admin_rf.get("/admin/users/user/", HTTP_REFERER=referer),
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == "/admin/users/user/?is_active__exact=1"


def test_referer_same_url(user_admin, admin_rf):
    """Test no apply if same referer."""
    response = user_admin.changelist_view(
        admin_rf.get("/admin/users/user/", HTTP_REFERER="/admin/users/user/"),
    )

    assert response.status_code == HTTPStatus.OK
