# -*- coding: utf-8 -*-

import graphene

from apps.users.services.user import metrics


class WorkItemUserMetricsType(graphene.ObjectType):
    """Work item user metrics type."""

    closed_spent = graphene.Float()
    opened_spent = graphene.Float()

    payroll_closed = graphene.Float()
    payroll_opened = graphene.Float()
    payroll = graphene.Float()

    taxes_closed = graphene.Float()
    taxes_opened = graphene.Float()
    taxes = graphene.Float()


class IssueUserMetricsType(WorkItemUserMetricsType):
    """Issue user metrics type."""

    opened_count = graphene.Int(resolver=metrics.issues_opened_count_resolver)


class MergeRequestUserMetricsType(WorkItemUserMetricsType):
    """Merge request user metrics type."""

    opened_count = graphene.Int(resolver=metrics.mr_opened_count_resolver)
