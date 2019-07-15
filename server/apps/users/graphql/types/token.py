from graphene_django import DjangoObjectType

from apps.users.models import Token


class TokenType(DjangoObjectType):
    class Meta:
        model = Token
        name = 'Token'
