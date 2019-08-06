import graphene

from .work_item_user_metrics import (
    IssueUserMetricsType, MergeRequestUserMetricsType
)


class UserMetricsType(graphene.ObjectType):
    payroll_closed = graphene.Float()
    payroll_opened = graphene.Float()
    bonus = graphene.Float()
    penalty = graphene.Float()
    issues = graphene.Field(IssueUserMetricsType)
    merge_requests = graphene.Field(MergeRequestUserMetricsType)
