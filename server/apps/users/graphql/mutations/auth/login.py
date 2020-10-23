from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from jnt_django_graphene_toolbox.security.permissions import AllowAny

from apps.users.graphql.mutations.inputs import LoginInput
from apps.users.graphql.types import TokenType
from apps.users.services.user.login import user_login


class LoginMutation(SerializerMutation):
    """Login mutation returns token."""

    class Meta:
        serializer_class = LoginInput

    permission_classes = (AllowAny,)

    token = graphene.Field(TokenType)

    @classmethod
    def perform_mutate(  # type: ignore
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data: Dict[str, Any],
    ) -> "LoginMutation":
        """After successful login return token."""
        token = user_login(
            validated_data["login"],
            validated_data["password"],
            info.context,
        )

        return cls(token=token)
