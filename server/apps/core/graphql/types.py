from graphene_django import DjangoObjectType
from graphene_permissions.mixins import AuthNode
from graphene_permissions.permissions import AllowAuthenticated


class BaseDjangoObjectType(AuthNode,
                           DjangoObjectType):
    permission_classes = (AllowAuthenticated,)

    class Meta:
        abstract = True
