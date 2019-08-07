import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.development.graphql.filters import MergeRequestFilterSet
from apps.development.graphql.resolvers import resolve_merge_requests_summary
from apps.development.graphql.types import (
    MergeRequestType, MergeRequestsSummaryType
)


class MergeRequestQueries(graphene.ObjectType):
    all_merge_requests = DataSourceConnectionField(
        MergeRequestType,
        filterset_class=MergeRequestFilterSet
    )
    merge_requests_summary = graphene.Field(
        MergeRequestsSummaryType,
        user=graphene.ID(),
        team=graphene.ID(),
        project=graphene.ID(),
        resolver=resolve_merge_requests_summary
    )
