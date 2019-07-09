import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType

from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.core.graphql.utils import is_field_selected
from apps.development.models import Issue
from apps.development.services.allowed.issues import filter_allowed_for_user
from apps.development.services.metrics.issue import get_issue_metrcis
from apps.development.services.problems.issue import get_issue_problems
from .issue_metrics import IssueMetricsType


class IssueType(DjangoObjectType):
    class Meta:
        model = Issue
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Issue'

    metrics = graphene.Field(IssueMetricsType)
    problems = graphene.List(graphene.String)

    def resolve_problems(self, info, **kwargs):
        return get_issue_problems(self)

    def resolve_metrics(self, info, **kwargs):
        return get_issue_metrcis(self)

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
