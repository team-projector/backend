import graphene

from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.users.graphql.types import UserType


class UsersQuery(graphene.ObjectType):
    user = DatasourceRelayNode.Field(UserType)
