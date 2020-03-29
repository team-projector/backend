# -*- coding: utf-8 -*-

from typing import Optional

from django.contrib.auth.models import AnonymousUser
from graphene.test import Client

from apps.core.utils.objects import dict2obj
from apps.users.models import Token, User
from apps.users.services.token.create import create_user_token
from gql import schema


class GraphQLClient(Client):
    """Test graphql client."""

    def __init__(self, *args, **kwargs) -> None:
        """Initializing."""
        super().__init__(schema, *args, **kwargs)

        self._user: Optional[User] = None
        self._token: Optional[Token] = None

    def set_user(self, user: User, token: Optional[Token] = None) -> None:
        """Set user for auth requests."""
        self._user = user

        if token is None:
            token = create_user_token(user)

        self._token = token

    def execute(self, *args, **kwargs):
        """Execute graphql request."""
        context = {
            "user": self._user or AnonymousUser(),
            "auth": self._token,
        }

        context.update(kwargs.get("extra_context", {}))

        kwargs["context_value"] = dict2obj(context)

        return super().execute(*args, **kwargs)
