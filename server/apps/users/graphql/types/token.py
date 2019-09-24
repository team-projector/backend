# -*- coding: utf-8 -*-

from apps.core.graphql.security.permissions import AllowAny
from apps.core.graphql.types import BaseDjangoObjectType
from apps.users.models import Token


class TokenType(BaseDjangoObjectType):
    permission_classes = (AllowAny,)

    class Meta:
        model = Token
        name = 'Token'
