import graphene
from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.core.graphql.utils import is_field_selected
from apps.development.graphql.types.interfaces import WorkItem
from apps.development.models import MergeRequest
from apps.development.services.allowed.merge_requests import \
    filter_allowed_for_user
from apps.development.services.metrics.merge_request import \
    get_merge_request_metrcis
from .merge_request_metrics import MergeRequestMetricsType


class MergeRequestType(BaseDjangoObjectType):
    metrics = graphene.Field(MergeRequestMetricsType)

    class Meta:
        model = MergeRequest
        interfaces = (DatasourceRelayNode, WorkItem)
        connection_class = DataSourceConnection
        name = 'MergeRequest'

    def resolve_metrics(self, info, **kwargs):
        return get_merge_request_metrcis(self)

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        queryset = filter_allowed_for_user(
            queryset,
            info.context.user
        )

        if is_field_selected(info, 'edges.node.user'):
            queryset = queryset.select_related('user')

        if is_field_selected(info, 'edges.node.participants'):
            queryset = queryset.prefetch_related('participants')

        if is_field_selected(info, 'edges.node.labels'):
            queryset = queryset.prefetch_related('labels')

        return queryset
