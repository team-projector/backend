from typing import Optional

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from social_core.actions import do_auth, do_complete
from social_django.compat import reverse
from social_django.utils import load_backend, load_strategy
from social_django.views import NAMESPACE, _do_login  # noqa: WPS450

from apps.users.models import Token


class SocialLoginService:
    """Handler for social authorization."""

    def begin_login(self, request: HttpRequest) -> str:
        """Start gitlab login."""
        request = self._prepare_request(request)

        response = do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)

        return response.url

    def complete_login(self, request, backend_data) -> Optional[Token]:
        """Completes user social authorization."""
        request = self._prepare_request(request)
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

    def _prepare_request(self, request: HttpRequest) -> HttpRequest:
        uri = reverse("{0}:complete".format(NAMESPACE), args=("gitlab",))
        request.social_strategy = load_strategy(request)
        request.strategy = getattr(
            request,
            "strategy",
            request.social_strategy,
        )
        request.backend = load_backend(request.social_strategy, "gitlab", uri)

        return request
