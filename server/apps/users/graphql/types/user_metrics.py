# -*- coding: utf-8 -*-

import graphene

from apps.users.graphql.types.work_item_user_metrics import (
    IssueUserMetricsType,
    MergeRequestUserMetricsType,
)
from apps.users.services.user import metrics


class UserMetricsType(graphene.ObjectType):
    """User metrics type."""

    payroll_closed = graphene.Float()
    payroll_opened = graphene.Float()
    payroll = graphene.Float()
    paid_work_breaks_days = graphene.Int(
        resolver=metrics.paid_work_breaks_days_resolver,
    )

    bonus = graphene.Float(resolver=metrics.bonus_resolver)
    penalty = graphene.Float(resolver=metrics.penalty_resolver)

    opened_spent = graphene.Float()
    closed_spent = graphene.Float()

    taxes_closed = graphene.Float()
    taxes_opened = graphene.Float()
    taxes = graphene.Float()

    issues = graphene.Field(IssueUserMetricsType)
    merge_requests = graphene.Field(MergeRequestUserMetricsType)

    last_salary_date = graphene.Date(resolver=metrics.last_salary_date_resolver)
