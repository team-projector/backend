import graphene

from apps.payroll.graphql.fields import AllSpentTimesConnectionField
from apps.payroll.graphql.resolvers import resolve_spent_times_summary
from apps.payroll.graphql.types import SpentTimesSummaryType


class TimeExpensesQueries(graphene.ObjectType):
    """Class represents list of available fields for spent times queries."""

    all_spent_times = AllSpentTimesConnectionField()
    spent_times_summary = graphene.Field(
        SpentTimesSummaryType,
        project=graphene.ID(),
        team=graphene.ID(),
        user=graphene.ID(),
        state=graphene.String(),
        date=graphene.Date(),
        salary=graphene.ID(),
        resolver=resolve_spent_times_summary,
    )
