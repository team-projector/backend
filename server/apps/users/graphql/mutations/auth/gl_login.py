# -*- coding: utf-8 -*-

import graphene
from django.contrib.auth import REDIRECT_FIELD_NAME
from social_core.actions import do_auth

from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.security.permissions import AllowAny
from apps.users.graphql.mutations.helpers.auth import page_social_auth


class LoginGitlabMutation(BaseMutation):
    """Login mutation through Gitlab returns url."""

    permission_classes = (AllowAny,)

    redirect_url = graphene.String()

    @classmethod
    def do_mutate(cls, root, info):  # noqa: WPS110
        """Returns url for Gitlab with app ID, callback url and state."""
        request = page_social_auth(info.context)

        response = do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)

        return LoginGitlabMutation(
            redirect_url=response.url,
        )
