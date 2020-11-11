from typing import Optional

from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from social_core.actions import do_complete
from social_django.views import _do_login  # noqa: WPS450

from apps.users.graphql.mutations.helpers.auth import page_social_auth
from apps.users.models import Token
from apps.users.services.token.create import create_user_token


def login_user(login: str, password: str, request) -> Token:
    """Login user."""
    if login and password:
        user = authenticate(request=request, login=login, password=password)

        if not user:
            raise AuthenticationFailed(
                _("MSG__UNABLE_TO_LOGIN_WITH_PROVIDED_CREDENTIALS"),
            )

        token = create_user_token(user)

        user.last_login = timezone.now()
        user.save(update_fields=("last_login",))

        return token  # noqa: WPS331

    raise AuthenticationFailed(_("MSG__MUST_INCLUDE_LOGIN_AND_PASSWORD"))


def logout_user(request) -> None:
    """Logout user."""
    request.auth.delete()


def complete_social_auth(request, backend_data) -> Optional[Token]:
    """Completes user social authorization."""
    request = page_social_auth(request)
    request.backend.set_data(**backend_data)

    complete_result = do_complete(
        request.backend,
        _do_login,
        user=None,
        redirect_name=REDIRECT_FIELD_NAME,
        request=request,
    )

    if isinstance(complete_result, Token):
        return complete_result

    raise AuthenticationFailed(_("MSG__AUTHENTICATION_ERROR"))
