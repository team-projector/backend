# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet

from apps.core import graphql
from apps.development.graphql.interfaces import WorkItem
from apps.development.graphql.types.issue_metrics import IssueMetricsType
from apps.development.models import Issue
from apps.development.services import issue as issue_service


class IssueType(graphql.BaseDjangoObjectType):
    """Issue type."""

    metrics = graphene.Field(IssueMetricsType)
    problems = graphene.List(graphene.String)

    class Meta:
        model = Issue
        filter_fields: list = []
        interfaces = (graphql.DatasourceRelayNode, WorkItem)
        connection_class = graphql.DataSourceConnection
        name = 'Issue'

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get issue problems."""
        return issue_service.get_problems(self)

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get issue metrics."""
        return issue_service.get_metrics(self)

    @classmethod
    def get_queryset(
        cls,
        queryset,
        info,  # noqa: WPS110
    ) -> QuerySet:
        """Get issues."""
        if isinstance(queryset, QuerySet):
            queryset = issue_service.filter_allowed_for_user(
                queryset,
                info.context.user,
            )

            if graphql.is_field_selected(info, 'edges.node.user'):
                queryset = queryset.select_related('user')

        return queryset
