import graphene
from django.db import models
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.core import graphql
from apps.development import models as development_models
from apps.development.graphql.interfaces import WorkItem
from apps.development.graphql.types.merge_request_metrics import (
    MergeRequestMetricsType,
)
from apps.development.services.merge_request.allowed import (
    filter_allowed_for_user,
)
from apps.development.services.merge_request.metrics import (
    get_merge_request_metrics,
)
from apps.development.services.merge_request.problems import (
    get_merge_request_problems,
)


class MergeRequestType(BaseDjangoObjectType):
    """Merge request type."""

    class Meta:
        model = development_models.MergeRequest
        interfaces = (DatasourceRelayNode, WorkItem)
        connection_class = DataSourceConnection
        name = "MergeRequest"

    metrics = graphene.Field(MergeRequestMetricsType)
    problems = graphene.List(graphene.String)

    @classmethod
    def get_queryset(cls, queryset, info) -> models.QuerySet:  # noqa: WPS110
        """Get queryset."""
        queryset = filter_allowed_for_user(queryset, info.context.user)

        if graphql.is_field_selected(info, "edges.node.user"):
            queryset = queryset.select_related("user")

        return queryset

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get merge request metrics."""
        return get_merge_request_metrics(self)

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get merge request problems."""
        return get_merge_request_problems(self)
