from typing import Optional

import graphene
from django.contrib.auth import REDIRECT_FIELD_NAME
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import BaseMutation
from social_core.actions import do_auth

from apps.users.graphql.mutations.helpers.auth import page_social_auth


class LoginGitlabMutation(BaseMutation):
    """Login mutation through Gitlab returns url."""

    redirect_url = graphene.String()

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
    ) -> "LoginGitlabMutation":
        """Returns redirect url for Gitlab."""
        request = page_social_auth(info.context)

        response = do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)

        return cls(redirect_url=response.url)
