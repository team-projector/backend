# -*- coding: utf-8 -*-

from typing import List

import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.core import graphql
from apps.development.graphql.interfaces import WorkItem
from apps.development.graphql.types.issue_metrics import IssueMetricsType
from apps.development.models import Issue
from apps.development.services.issue import allowed, metrics
from apps.development.services.issue.problems import get_issue_problems


class IssueType(BaseDjangoObjectType):
    """Issue type."""

    class Meta:
        model = Issue
        filter_fields: List[str] = []
        interfaces = (DatasourceRelayNode, WorkItem)
        connection_class = DataSourceConnection
        name = "Issue"

    metrics = graphene.Field(IssueMetricsType)
    problems = graphene.List(graphene.String)
    time_spent = graphene.Field(graphene.Int)

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get issues."""
        if isinstance(queryset, list):
            return queryset

        queryset = allowed.filter_allowed_for_user(queryset, info.context.user)

        if graphql.is_field_selected(info, "edges.node.user"):
            queryset = queryset.select_related("user")

        return queryset

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get issue problems."""
        return get_issue_problems(self)

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get issue metrics."""
        return metrics.get_issue_metrics(self)

    def resolve_time_spent(self, info, **kwargs):  # noqa: WPS110
        """Get user time spent."""
        if self.user:
            return metrics.get_user_time_spent(self, user=self.user)
        return 0
