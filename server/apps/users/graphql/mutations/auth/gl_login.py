from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import BaseMutation

from apps.core import injector
from apps.users.services.auth.social_login import SocialLoginService


class LoginGitlabMutation(BaseMutation):
    """Login mutation through Gitlab returns url."""

    redirect_url = graphene.String()

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ) -> "LoginGitlabMutation":
        """Returns redirect url for Gitlab."""
        service = injector.get(SocialLoginService)
        redirect_url = service.begin_login(info.context)
        return cls(redirect_url=redirect_url)
