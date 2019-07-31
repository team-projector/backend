import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.development.graphql.filters import MergeRequestFilterSet
from apps.development.graphql.types import MergeRequestType


class MergeRequestQueries(graphene.ObjectType):
    all_merge_requests = DataSourceConnectionField(
        MergeRequestType,
        filterset_class=MergeRequestFilterSet
    )
