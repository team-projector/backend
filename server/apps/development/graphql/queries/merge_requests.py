import graphene

from apps.development.graphql.fields import AllMergeRequestsConnectionField
from apps.development.graphql.resolvers import resolve_merge_requests_summary
from apps.development.graphql.types import MergeRequestsSummaryType


class MergeRequestQueries(graphene.ObjectType):
    """Class represents list of available fields for merge request queries."""

    all_merge_requests = AllMergeRequestsConnectionField()
    merge_requests_summary = graphene.Field(
        MergeRequestsSummaryType,
        user=graphene.ID(),
        team=graphene.ID(),
        project=graphene.ID(),
        state=graphene.String(),
        resolver=resolve_merge_requests_summary,
    )
