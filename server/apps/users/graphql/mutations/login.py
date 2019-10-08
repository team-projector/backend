# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.security.permissions import AllowAny
from apps.users.graphql.types import TokenType
from apps.users.services.auth import login_user


class LoginMutation(BaseMutation):
    """Login mutation returns token."""

    permission_classes = (AllowAny,)

    token = graphene.Field(TokenType)

    class Arguments:
        login = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def do_mutate(cls, root, info, login, password):
        """After successful login return token."""
        token = login_user(
            login,
            password,
            info.context,
        )

        return LoginMutation(
            token=token,
        )
