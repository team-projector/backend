import pytest
from rest_framework.exceptions import AuthenticationFailed
from social_core.backends.gitlab import GitLabOAuth2

from apps.users.models import Token

KEY_TOKEN_TYPE = "token_type"
KEY_EXPIRES_IN = "expires_in"
KEY_ACCESS_TOKEN = "access_token"
KEY_REFRESH_TOKEN = "refresh_token"

ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"


def test_complete_login(
    user,
    gl_mocker,
    complete_gl_auth_mutation,
    gl_token_request_info,
):
    """Test complete login."""
    gl_mocker.register_get(
        "/user",
        {"id": user.pk, "username": user.login, "email": user.email},
    )

    gl_mocker.base_api_url = GitLabOAuth2.ACCESS_TOKEN_URL
    gl_mocker.register_post(
        "",
        {
            KEY_ACCESS_TOKEN: ACCESS_TOKEN,
            KEY_REFRESH_TOKEN: REFRESH_TOKEN,
            KEY_TOKEN_TYPE: "bearer",
            KEY_EXPIRES_IN: 7200,
        },
    )

    response = complete_gl_auth_mutation(
        root=None,
        info=gl_token_request_info,
        code="test_code",
        state=gl_token_request_info.context.session["gitlab_state"],
    )

    assert Token.objects.filter(pk=response.token.pk, user=user).exists()


def test_user_not_in_system(
    db,
    gl_mocker,
    complete_gl_auth_mutation,
    gl_token_request_info,
):
    """Test complete login."""
    gl_mocker.register_get(
        "/user",
        {"id": 1, "username": "user", "email": "user@mail.ru"},
    )

    gl_mocker.base_api_url = GitLabOAuth2.ACCESS_TOKEN_URL
    gl_mocker.register_post(
        "",
        {
            KEY_ACCESS_TOKEN: ACCESS_TOKEN,
            KEY_REFRESH_TOKEN: REFRESH_TOKEN,
            KEY_TOKEN_TYPE: "bearer",
            KEY_EXPIRES_IN: 7200,
        },
    )

    with pytest.raises(AuthenticationFailed):
        complete_gl_auth_mutation(
            root=None,
            info=gl_token_request_info,
            code="test_code",
            state=gl_token_request_info.context.session["gitlab_state"],
        )


def test_not_login(
    user,
    gl_mocker,
    complete_gl_auth_mutation,
    gl_token_request_info,
):
    """Test not login user."""
    gl_mocker.register_get(
        "/user",
        {"id": user.pk, "username": "test_user", "email": user.email},
    )

    gl_mocker.base_api_url = GitLabOAuth2.ACCESS_TOKEN_URL
    gl_mocker.register_post(
        "",
        {
            KEY_ACCESS_TOKEN: ACCESS_TOKEN,
            KEY_REFRESH_TOKEN: REFRESH_TOKEN,
            KEY_TOKEN_TYPE: "bearer",
            KEY_EXPIRES_IN: 7200,
        },
    )

    with pytest.raises(AuthenticationFailed):
        complete_gl_auth_mutation(
            root=None,
            info=gl_token_request_info,
            code="test_code",
            state=gl_token_request_info.context.session["gitlab_state"],
        )
