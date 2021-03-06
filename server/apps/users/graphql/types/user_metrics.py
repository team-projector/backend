import graphene

from apps.users.graphql.types.work_item_user_metrics import (
    IssueUserMetricsType,
    MergeRequestUserMetricsType,
)


class UserMetricsType(graphene.ObjectType):
    """User metrics type."""

    payroll_closed = graphene.Float()
    payroll_opened = graphene.Float()
    payroll = graphene.Float()
    paid_work_breaks_days = graphene.Int()

    bonus = graphene.Float()
    penalty = graphene.Float()

    opened_spent = graphene.Float()
    closed_spent = graphene.Float()

    taxes_closed = graphene.Float()
    taxes_opened = graphene.Float()
    taxes = graphene.Float()

    issues = graphene.Field(IssueUserMetricsType)
    merge_requests = graphene.Field(MergeRequestUserMetricsType)

    last_salary_date = graphene.Date()
