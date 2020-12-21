from typing import Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.security.permissions import AllowAny
from rest_framework import serializers

from apps.core.graphql.mutations import (
    BaseMutationPresenter,
    BaseUseCaseMutation,
)
from apps.users.application.use_cases.users import (
    LoginInputDto,
    LoginOutputDto,
    LoginUseCase,
)
from apps.users.graphql.types import TokenType


class LoginInputSerializer(serializers.Serializer):
    """InputSerializer."""

    login = serializers.CharField()
    password = serializers.CharField()


class LoginPresenter(BaseMutationPresenter[LoginOutputDto]):
    """Login presenter."""

    def get_response_data(self) -> Dict[str, object]:
        """Returns response fields."""
        return {
            "token": self.output_dto.token,
        }


class LoginMutation(BaseUseCaseMutation):
    """Login mutation returns token."""

    class Meta:
        permission_classes = (AllowAny,)
        serializer_class = LoginInputSerializer
        use_case_class = LoginUseCase
        presenter_class = LoginPresenter

    token = graphene.Field(TokenType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> LoginInputDto:
        """Returns dto for use case."""
        return LoginInputDto(
            username=validated_data["login"],
            password=validated_data["password"],
        )
