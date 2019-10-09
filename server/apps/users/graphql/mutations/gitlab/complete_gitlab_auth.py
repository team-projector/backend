# -*- coding: utf-8 -*-

import graphene
from django.contrib.auth import REDIRECT_FIELD_NAME
from social_core.actions import do_complete
from social_django.views import _do_login  # noqa WPS436

from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.security.permissions import AllowAny
from apps.users.graphql.types import TokenType

from .auth import psa


class CompleteGitlabAuthMutation(BaseMutation):
    """Complete login mutation after redirection from Gitlab."""

    permission_classes = (AllowAny,)

    token = graphene.Field(TokenType)

    class Arguments:
        code = graphene.String(required=True)
        state = graphene.String(required=True)

    @classmethod
    def do_mutate(cls, root, info, code, state):
        """After successful login return token."""
        request = psa(info.context)
        request.backend.set_data(code=code, state=state)

        token = do_complete(
            request.backend,
            _do_login,
            user=None,
            redirect_name=REDIRECT_FIELD_NAME,
            request=request,
        )

        return CompleteGitlabAuthMutation(
            token=token,
        )
