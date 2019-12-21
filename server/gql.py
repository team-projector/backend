# -*- coding: utf-8 -*-

import graphene
from graphene_django.debug import DjangoDebug

from apps.core.graphql.views import ApiGraphQLView, PlaygroundGraphQLView
from apps.development.graphql.mutations import DevelopmentMutations
from apps.development.graphql.queries import DevelopmentQueries
from apps.payroll.graphql.mutations import WorkBreaksMutations
from apps.payroll.graphql.queries import (
    SalariesQueries,
    TimeExpensesQueries,
    WorkBreaksQueries,
)
from apps.users.graphql.mutations import AuthMutations
from apps.users.graphql.queries import UsersQueries


class Query(  # noqa: WPS215
    DevelopmentQueries,
    TimeExpensesQueries,
    SalariesQueries,
    WorkBreaksQueries,
    UsersQueries,
    graphene.ObjectType,
):
    """Class representing all available queries."""

    debug = graphene.Field(
        DjangoDebug,
        name='_debug',
    )


class Mutation(  # noqa: WPS215
    DevelopmentMutations,
    WorkBreaksMutations,
    AuthMutations,
    graphene.ObjectType,
):
    """Class representing all available mutations."""


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
)


def get_api_graphql_view():
    """Get API graphql view."""
    return ApiGraphQLView.as_view(
        schema=schema,
    )


def get_graphql_view():
    """Get graphql view."""
    return PlaygroundGraphQLView.as_view(
        graphiql=True,
        schema=schema,
    )
