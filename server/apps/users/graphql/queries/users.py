import graphene

from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.users.graphql.resolvers import resolve_me_user
from apps.users.graphql.types import UserType


class UsersQueries(graphene.ObjectType):
    user = DatasourceRelayNode.Field(UserType)
    me_user = graphene.Field(UserType, resolver=resolve_me_user)
