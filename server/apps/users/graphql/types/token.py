import graphene
from jnt_django_graphene_toolbox.types import BaseModelObjectType

from apps.users.models import Token


class TokenType(BaseModelObjectType):
    """Token type."""

    class Meta:
        model = Token

    key = graphene.String()
    created = graphene.DateTime()
