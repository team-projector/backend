import graphene
from graphene_django.debug import DjangoDebug

from apps.core.graphql.views import (
    DrfAuthenticatedGraphQLView,
    PrivateGraphQLView
)
from apps.development.graphql.query import IssuesQuery, TeamsQuery
from apps.users.graphql.query import UsersQuery


class Query(IssuesQuery,
            TeamsQuery,
            UsersQuery,
            graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='_debug')


schema = graphene.Schema(
    query=Query
)


def get_api_graphql_view():
    return DrfAuthenticatedGraphQLView.as_view(
        graphiql=True,
        schema=schema
    )


def get_graphql_view():
    return PrivateGraphQLView.as_view(
        graphiql=True,
        schema=schema
    )
