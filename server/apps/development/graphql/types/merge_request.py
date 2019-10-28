# -*- coding: utf-8 -*-

import graphene
from django.contrib.auth import get_user_model
from django.db import models

from apps.core import graphql
from apps.development import graphql as development_graphql
from apps.development import models as development_models
from apps.development.graphql.interfaces import WorkItem
from apps.development.graphql.types.merge_request_metrics import (
    MergeRequestMetricsType,
)
from apps.development.services import merge_request as merge_request_service
from apps.users.graphql.types import UserType


class MergeRequestType(graphql.BaseDjangoObjectType):
    """Merge request type."""

    metrics = graphene.Field(MergeRequestMetricsType)
    problems = graphene.List(graphene.String)

    class Meta:
        model = development_models.MergeRequest
        interfaces = (graphql.DatasourceRelayNode, WorkItem)
        connection_class = graphql.DataSourceConnection
        name = 'MergeRequest'

    def resolve_metrics(self, info, **kwargs):  # noqa WPS110
        """Get merge request metrics."""
        return merge_request_service.get_metrics(self)

    def resolve_problems(self, info, **kwargs):  # noqa WPS110
        """Get merge request problems."""
        return merge_request_service.get_problems(self)

    def resolve_participants(self, info, **kwargs):  # noqa WPS110
        """Get merge request participants."""
        return getattr(self, '_participants_', self.participants)

    def resolve_labels(self, info, **kwargs):  # noqa WPS110
        """Get merge request labels."""
        return getattr(self, '_labels_', self.labels)

    def resolve_issues(self, info, **kwargs):  # noqa WPS110
        """Get merge request issues."""
        return getattr(self, '_issues_', self.issues)

    @classmethod
    def get_queryset(cls, queryset, info) -> models.QuerySet:  # noqa WPS110
        """Get queryset."""
        queryset = merge_request_service.filter_allowed_for_user(
            queryset,
            info.context.user,
        )

        if graphql.is_field_selected(info, 'edges.node.user'):
            queryset = queryset.select_related('user')

        # TODO: condsider using graphene_django_optimizer here
        if graphql.is_field_selected(info, 'edges.node.participants'):
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
