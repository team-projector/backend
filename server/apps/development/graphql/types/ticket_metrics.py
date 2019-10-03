# -*- coding: utf-8 -*-

import graphene

from .issues_container_metrics import IssuesContainerMetricsType


class TicketMetricsType(IssuesContainerMetricsType):
    """
    A class representing ticket metrics fields.
    """
    budget_estimate = graphene.Float()
    budget_spent = graphene.Float()
    budget_remains = graphene.Float()
    payroll = graphene.Float()
    profit = graphene.Float()
