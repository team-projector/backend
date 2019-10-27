# -*- coding: utf-8 -*-

import graphene
from django.contrib.auth import get_user_model
from django.db.models import Prefetch, QuerySet

from apps.core import graphql
from apps.development.graphql.interfaces import WorkItem
from apps.development.graphql.types.issue_metrics import IssueMetricsType
from apps.development.models import Issue, Label
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

    def resolve_problems(self, info, **kwargs):  # noqa WPS110
        """Get issue problems."""
        return issue_service.get_problems(self)

    def resolve_metrics(self, info, **kwargs):  # noqa WPS110
        """Get issue metrics."""
        return issue_service.get_metrics(self)

    def resolve_participants(self, info, **kwargs):  # noqa WPS110
        """Get issue participants."""
        return getattr(self, '_participants_', self.participants)

    def resolve_labels(self, info, **kwargs):  # noqa WPS110
        """Get issue labels."""
        return getattr(self, '_labels_', self.labels)

    @classmethod
    def get_queryset(
        cls,
        queryset,
        info,  # noqa WPS110
    ) -> QuerySet:
        """Get issues."""
        queryset = issue_service.filter_allowed_for_user(
            queryset,
            info.context.user,
        )

        if graphql.is_field_selected(info, 'edges.node.user'):
            queryset = queryset.select_related('user')

        # TODO: condsider using graphene_django_optimizer here
        if graphql.is_field_selected(info, 'edges.node.participants'):
            from apps.users.graphql.types import UserType

            users = get_user_model().objects
            queryset = queryset.prefetch_related(Prefetch(
                'participants',
                queryset=UserType.get_queryset(users, info).all(),
                to_attr='_participants_',
            ))

        # TODO: condsider using graphene_django_optimizer here
        if graphql.is_field_selected(info, 'edges.node.labels'):
            from apps.development.graphql.types import LabelType

            queryset = queryset.prefetch_related(Prefetch(
                'labels',
                queryset=LabelType.get_queryset(Label.objects, info).all(),
                to_attr='_labels_',
            ))

        return queryset
