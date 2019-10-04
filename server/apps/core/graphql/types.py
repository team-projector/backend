# -*- coding: utf-8 -*-

from graphene_django import DjangoObjectType

from apps.core.graphql.security.mixins.node import AuthNode
from apps.core.graphql.security.permissions import AllowAuthenticated


class BaseDjangoObjectType(
    AuthNode,
    DjangoObjectType,
):
    """
    A base class Django object type.
    """
    permission_classes = (AllowAuthenticated,)

    class Meta:
        abstract = True
