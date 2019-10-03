# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.graphql.resolvers import resolve_spent_times_summary
from apps.payroll.graphql.types import SpentTimesSummaryType, SpentTimeType


class TimeExpensesQueries(graphene.ObjectType):
    """
    Class representing list of available fields for spent times queries.
    """
    all_spent_times = DataSourceConnectionField(
        SpentTimeType,
        filterset_class=SpentTimeFilterSet,
    )

    spent_times_summary = graphene.Field(
        SpentTimesSummaryType,
        project=graphene.ID(),
        team=graphene.ID(),
        user=graphene.ID(),
        state=graphene.String(),
        date=graphene.Date(),
        resolver=resolve_spent_times_summary,
    )
