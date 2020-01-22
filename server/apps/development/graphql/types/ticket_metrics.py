# -*- coding: utf-8 -*-

import graphene

from apps.development.graphql.types.issues_container_metrics import (
    IssuesContainerMetricsType,
)


class TicketMetricsType(IssuesContainerMetricsType):
    """Ticket metrics type."""

    budget_estimate = graphene.Float()
    budget_spent = graphene.Float()
    budget_remains = graphene.Float()
    payroll = graphene.Float()
    profit = graphene.Float()
    opened_time_remains = graphene.Int()
