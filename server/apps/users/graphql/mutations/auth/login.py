from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.errors import GraphQLInputError
from jnt_django_graphene_toolbox.mutations import BaseMutation
from rest_framework import serializers

from apps.core import injector
from apps.core.graphql.mutations.mixins import ErrorHandlerMixin
from apps.users.graphql.types import TokenType
from apps.users.services.auth.login import LoginInputDto, LoginService


class InputSerializer(serializers.Serializer):
    """InputSerializer."""

    login = serializers.CharField()
    password = serializers.CharField()


class LoginMutation(ErrorHandlerMixin, BaseMutation):
    """Login mutation returns token."""

    class Arguments:
        login = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.Field(TokenType)

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ) -> "LoginMutation":
        """Login user."""
        serializer = InputSerializer(data=kwargs)
        if not serializer.is_valid():
            return GraphQLInputError(serializer.errors)

        service = injector.get(LoginService)

        token = service.execute(
            LoginInputDto(
                username=serializer.validated_data["login"],
                password=serializer.validated_data["password"],
            ),
        )
        return cls(token=token)
