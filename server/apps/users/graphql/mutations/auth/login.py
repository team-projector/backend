from typing import Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from rest_framework import serializers

from apps.core import injector
from apps.core.graphql.mutations.mixins import ErrorHandlerMixin
from apps.users.graphql.types import TokenType
from apps.users.services.login import LoginInputDto, LoginService


class LoginInputSerializer(serializers.Serializer):
    """InputSerializer."""

    login = serializers.CharField()
    password = serializers.CharField()


class LoginMutation(ErrorHandlerMixin, SerializerMutation):
    """Login mutation returns token."""

    class Meta:
        serializer_class = LoginInputSerializer

    token = graphene.Field(TokenType)

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data: Dict[str, str],
    ) -> "LoginMutation":
        """Login user."""
        service = injector.get(LoginService)
        token = service.execute(
            LoginInputDto(
                username=validated_data["login"],
                password=validated_data["password"],
            ),
        )
        return cls(token=token)
