from social_core.backends.gitlab import GitLabOAuth2

from apps.users.models import Token


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
            "access_token": "access_token",
            "token_type": "bearer",
            "expires_in": 7200,
            "refresh_token": "refresh_token",
        },
    )

    response = complete_gl_auth_mutation(
        root=None,
        info=gl_token_request_info,
        code="test_code",
        state=gl_token_request_info.context.session["gitlab_state"],
    )

    assert Token.objects.filter(pk=response.token.pk, user=user).exists()


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
            "access_token": "access_token",
            "token_type": "bearer",
            "expires_in": 7200,
            "refresh_token": "refresh_token",
        },
    )

    response = complete_gl_auth_mutation(
        root=None,
        info=gl_token_request_info,
        code="test_code",
        state=gl_token_request_info.context.session["gitlab_state"],
    )

    assert not response.token
