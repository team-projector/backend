from typing import Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import BaseSerializerMutation
from rest_framework import serializers

from apps.core import injector
from apps.users.graphql.types import TokenType
from apps.users.services.auth.social_login import SocialLoginService


class InputSerializer(serializers.Serializer):
    """InputSerializer."""

    code = serializers.CharField()
    state = serializers.CharField()


class CompleteGitlabAuthMutation(BaseSerializerMutation):
    """Complete login mutation after redirection from Gitlab."""

    class Meta:
        serializer_class = InputSerializer

    token = graphene.Field(TokenType)

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data: Dict[str, str],
    ) -> "CompleteGitlabAuthMutation":
        """After successful login return class with token."""
        service = injector.get(SocialLoginService)
        token = service.complete_login(info.context, validated_data)
        return cls(token=token)
