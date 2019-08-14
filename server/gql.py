import graphene
from graphene_django.debug import DjangoDebug

from apps.core.graphql.views import PlaygroundGraphQLView, ApiGraphQLView
from apps.development.graphql.mutations import (
    IssuesMutations, MilestonesMutations
)
from apps.development.graphql.queries import (
    IssuesQueries, MergeRequestQueries, MilestonesQueries, ProjectsQueries,
    TeamsQueries, GitlabQueries
)
from apps.payroll.graphql.mutations import WorkBreaksMutations
from apps.payroll.graphql.queries import (
    TimeExpensesQueries, SalariesQueries, WorkBreakQueries
)
from apps.users.graphql.mutations import AuthMutations
from apps.users.graphql.queries import UsersQueries


class Query(IssuesQueries,
            MergeRequestQueries,
            MilestonesQueries,
            ProjectsQueries,
            TeamsQueries,
            GitlabQueries,
            TimeExpensesQueries,
            SalariesQueries,
            WorkBreakQueries,
            UsersQueries,
            graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='_debug')


class Mutation(IssuesMutations,
               MilestonesMutations,
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
        schema=schema
    )


def get_graphql_view():
    return PlaygroundGraphQLView.as_view(
        graphiql=True,
        schema=schema
    )
