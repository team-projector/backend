import graphene

from apps.core.graphql.views import (
    DrfAuthenticatedGraphQLView,
    PrivateGraphQLView
)
from apps.development.graphql.query.issues import IssuesQuery


class Query(IssuesQuery,
            graphene.ObjectType):
    pass


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
