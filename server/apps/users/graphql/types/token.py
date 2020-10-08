from jnt_django_graphene_toolbox.security.permissions import AllowAny
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.users.models import Token


class TokenType(BaseDjangoObjectType):
    """Token type."""

    class Meta:
        model = Token
        name = "Token"

    permission_classes = (AllowAny,)
