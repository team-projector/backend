# -*- coding: utf-8 -*-

from typing import List

import graphene
from django.db.models import QuerySet

from apps.core import graphql
from apps.development.graphql.interfaces import WorkItem
from apps.development.graphql.types.issue_metrics import IssueMetricsType
from apps.development.models import Issue
from apps.development.services.issue.allowed import filter_allowed_for_user
from apps.development.services.issue.metrics import (
    get_issue_metrics,
    get_user_time_spent,
)
from apps.development.services.issue.problems import get_issue_problems


class IssueType(graphql.BaseDjangoObjectType):
    """Issue type."""

    class Meta:
        model = Issue
        filter_fields: List[str] = []
        interfaces = (graphql.DatasourceRelayNode, WorkItem)
        connection_class = graphql.DataSourceConnection
        name = "Issue"

    metrics = graphene.Field(IssueMetricsType)
    problems = graphene.List(graphene.String)
    time_spent = graphene.Field(graphene.Int)

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get issues."""
        if isinstance(queryset, list):
            return queryset

        queryset = filter_allowed_for_user(queryset, info.context.user)

        if graphql.is_field_selected(info, "edges.node.user"):
            queryset = queryset.select_related("user")

        return queryset

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get issue problems."""
        return get_issue_problems(self)

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get issue metrics."""
        return get_issue_metrics(self)

    def resolve_time_spent(self, info, **kwargs):  # noqa: WPS110
        """Get user time spent."""
        if self.user:
            return get_user_time_spent(self, user=self.user)
        return 0
