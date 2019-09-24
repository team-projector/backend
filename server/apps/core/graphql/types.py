# -*- coding: utf-8 -*-

from graphene_django_optimizer import OptimizedDjangoObjectType

from apps.core.graphql.security.mixins.node import AuthNode
from apps.core.graphql.security.permissions import AllowAuthenticated


class BaseDjangoObjectType(AuthNode,
                           OptimizedDjangoObjectType):
    permission_classes = (AllowAuthenticated,)

    class Meta:
        abstract = True
