import graphene
from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.types.issues_container_metrics import (
    IssuesContainerMetricsType
)
from apps.development.models import Feature
from apps.development.services.allowed.features import filter_allowed_for_user
from apps.development.services.metrics.feature import get_feature_metrics


class FeatureType(BaseDjangoObjectType):
    metrics = graphene.Field(IssuesContainerMetricsType)

    class Meta:
        model = Feature
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Feature'

    def resolve_metrics(self, info, **kwargs):
        return get_feature_metrics(self)

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        queryset = filter_allowed_for_user(
            queryset,
            info.context.user
        )

        return queryset
