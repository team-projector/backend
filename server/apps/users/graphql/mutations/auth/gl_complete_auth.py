from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.errors import GraphQLInputError
from jnt_django_graphene_toolbox.mutations import BaseMutation
from rest_framework import serializers

from apps.core import injector
from apps.users.graphql.types import TokenType
from apps.users.services.auth.social_login import SocialLoginService


class InputSerializer(serializers.Serializer):
    """InputSerializer."""

    code = serializers.CharField()
    state = serializers.CharField()


class CompleteGitlabAuthMutation(BaseMutation):
    """Complete login mutation after redirection from Gitlab."""

    class Arguments:
        code = graphene.String(required=True)
        state = graphene.String(required=True)

    token = graphene.Field(TokenType)

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ) -> "CompleteGitlabAuthMutation":
        """After successful login return class with token."""
        serializer = InputSerializer(data=kwargs)
        if not serializer.is_valid():
            return GraphQLInputError(serializer.errors)

        service = injector.get(SocialLoginService)
        token = service.complete_login(info.context, serializer.validated_data)
        return cls(token=token)
