# -*- coding: utf-8 -*-

import graphene
from graphene_django.debug import DjangoDebug

from apps.core.graphql.views import (
    PlaygroundGraphQLView,
    ApiGraphQLView,
)
from apps.development.graphql.mutations import (
    IssuesMutations,
    MilestonesMutations,
    TicketsMutations,
)
from apps.development.graphql.queries import (
    IssuesQueries,
    MergeRequestQueries,
    MilestonesQueries,
    ProjectsQueries,
    TeamsQueries,
    TicketsQueries,
    GitlabQueries,
)
from apps.payroll.graphql.mutations import WorkBreaksMutations
from apps.payroll.graphql.queries import (
    TimeExpensesQueries,
    SalariesQueries,
    WorkBreaksQueries,
)
from apps.users.graphql.mutations import AuthMutations
from apps.users.graphql.queries import UsersQueries


class Query(IssuesQueries,
            TicketsQueries,
            MergeRequestQueries,
            MilestonesQueries,
            ProjectsQueries,
            TeamsQueries,
            GitlabQueries,
            TimeExpensesQueries,
            SalariesQueries,
            WorkBreaksQueries,
            UsersQueries,
            graphene.ObjectType):
    debug = graphene.Field(
        DjangoDebug,
        name='_debug',
    )


class Mutation(IssuesMutations,
               MilestonesMutations,
               TicketsMutations,
               WorkBreaksMutations,
               AuthMutations,
               graphene.ObjectType):
    pass


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
)


def get_api_graphql_view():
    return ApiGraphQLView.as_view(
        schema=schema,
    )


def get_graphql_view():
    return PlaygroundGraphQLView.as_view(
        graphiql=True,
        schema=schema,
    )
