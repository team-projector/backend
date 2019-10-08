# -*- coding: utf-8 -*-

import graphene
from django.contrib.auth import get_user_model
from django.db import models

from apps.core import graphql
from apps.development import models as development_models
from apps.development.services.allowed.merge_requests import (
    filter_allowed_for_user,
)
from apps.development.services.metrics.merge_request import (
    get_merge_request_metrcis,
)
from apps.development.services.problems.merge_request import (
    get_merge_request_problems,
)

from ... import graphql as development_graphql
from .interfaces import WorkItem
from .merge_request_metrics import MergeRequestMetricsType


class MergeRequestType(graphql.BaseDjangoObjectType):
    """Merge request type."""

    metrics = graphene.Field(MergeRequestMetricsType)
    problems = graphene.List(graphene.String)

    class Meta:
        model = development_models.MergeRequest
        interfaces = (graphql.DatasourceRelayNode, WorkItem)
        connection_class = graphql.DataSourceConnection
        name = 'MergeRequest'

    def resolve_metrics(self, info, **kwargs):
        """Get merge request metrics."""
        return get_merge_request_metrcis(self)

    def resolve_problems(self, info, **kwargs):
        """Get merge request problems."""
        return get_merge_request_problems(self)

    def resolve_participants(self, info, **kwargs):
        """Get merge request participants."""
        return getattr(self, '_participants_', self.participants)

    def resolve_labels(self, info, **kwargs):
        """Get merge request labels."""
        return getattr(self, '_labels_', self.labels)

    def resolve_issues(self, info, **kwargs):
        """Get merge request issues."""
        return getattr(self, '_issues_', self.issues)

    @classmethod
    def get_queryset(cls, queryset, info) -> models.QuerySet:
        """Get queryset."""
        queryset = filter_allowed_for_user(
            queryset,
            info.context.user,
        )

        if graphql.is_field_selected(info, 'edges.node.user'):
            queryset = queryset.select_related('user')

        # TODO: condsider using graphene_django_optimizer here
        if graphql.is_field_selected(info, 'edges.node.participants'):
            from apps.users.graphql.types import UserType

            users = get_user_model().objects
            queryset = queryset.prefetch_related(models.Prefetch(
                'participants',
                queryset=UserType.get_queryset(users, info).all(),
                to_attr='_participants_',
            ))

        # TODO: condsider using graphene_django_optimizer here
        if graphql.is_field_selected(info, 'edges.node.labels'):
            queryset = queryset.prefetch_related(models.Prefetch(
                'labels',
                queryset=development_graphql.types.LabelType.get_queryset(
                    development_models.Label.objects, info,
                ).all(),
                to_attr='_labels_',
            ))

        # TODO: condsider using graphene_django_optimizer here
        if graphql.is_field_selected(info, 'edges.node.issues'):
            queryset = queryset.prefetch_related(models.Prefetch(
                'issues',
                queryset=development_graphql.types.IssueType.get_queryset(
                    development_models.Issue.objects, info,
                ).all(),
                to_attr='_issues_',
            ))

        return queryset
