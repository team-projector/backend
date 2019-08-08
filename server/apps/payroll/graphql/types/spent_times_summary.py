import graphene

from apps.development.graphql.types.issues_summary import IssuesSummaryType
from apps.development.graphql.types.merge_requests_summary import \
    MergeRequestsSummaryType


class IssuesSpentTimesSummaryType(IssuesSummaryType):
    spent = graphene.Int()


class MergeRequestsSpentTimesSummaryType(MergeRequestsSummaryType):
    spent = graphene.Int()


class SpentTimesSummaryType(graphene.ObjectType):
    spent = graphene.Int()
    issues = graphene.Field(IssuesSpentTimesSummaryType)
    merge_requests = graphene.Field(MergeRequestsSpentTimesSummaryType)
