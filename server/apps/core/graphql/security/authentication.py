from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication as DrfTokenAuth

from apps.users.models import Token


class TokenAuthentication(DrfTokenAuth):
    """Token based authentication."""

    keyword = "Bearer"
    model = Token

    def authenticate_credentials(self, key: str):
        """Get user and token by token key."""
        user, token = super().authenticate_credentials(key)

        if self._is_expired(token):
            raise exceptions.AuthenticationFailed("Token has expired")

        return user, token

    def _is_expired(self, token) -> bool:
        """
        Is expired.

        :param token:
        :rtype: bool
        """
        return token.created < timezone.now() - timedelta(
            minutes=settings.TOKEN_EXPIRE_PERIOD,
        )


def auth_required(info: ResolveInfo) -> None:  # noqa: WPS110
    """Check user is auth."""
    user = getattr(info.context, "user", None) or AnonymousUser

    if any([not user.is_active, user.is_anonymous]):
        raise GraphQLPermissionDenied
