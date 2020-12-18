from typing import Optional

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from social_core.actions import do_complete
from social_django.views import _do_login  # noqa: WPS450

from apps.users.graphql.mutations.helpers.auth import page_social_auth
from apps.users.models import Token


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
