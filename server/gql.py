import graphene
from graphene_django.debug import DjangoDebug
from jnt_django_graphene_toolbox import scheme, views

from apps.core.graphql.views import ApiGraphQLView
from apps.development.graphql.mutations import DevelopmentMutations
from apps.development.graphql.queries import DevelopmentQueries
from apps.payroll.graphql.mutations import PayrollMutations
from apps.payroll.graphql.queries import PayrollQueries
from apps.users.graphql.mutations import UsersMutations
from apps.users.graphql.queries import UsersQueries


class Query(  # noqa: WPS215
    DevelopmentQueries,
    PayrollQueries,
    UsersQueries,
    graphene.ObjectType,
):
    """Class representing all available queries."""

    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutation(  # noqa: WPS215
    DevelopmentMutations,
    PayrollMutations,
    UsersMutations,
    graphene.ObjectType,
):
    """Class representing all available mutations."""


schema = scheme.Schema(query=Query, mutation=Mutation)


def get_api_graphql_view():
    """Get API graphql view."""
    return ApiGraphQLView.as_view(schema=schema)


def get_graphql_view():
    """Get graphql view."""
    return views.PlaygroundGraphQLView.as_view(graphiql=True, schema=schema)
