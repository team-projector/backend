# -*- coding: utf-8 -*-

import graphene
from django.contrib.auth import get_user_model
from django.db.models import Prefetch, QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.core.graphql.utils import is_field_selected
from apps.development.graphql.types.interfaces import WorkItem
from apps.development.models import Issue, Label, MergeRequest
from apps.development.services.allowed.merge_requests import (
    filter_allowed_for_user,
)
from apps.development.services.metrics.merge_request import (
    get_merge_request_metrcis,
)
from apps.development.services.problems.merge_request import (
    get_merge_request_problems,
)

from .merge_request_metrics import MergeRequestMetricsType


class MergeRequestType(BaseDjangoObjectType):
    """
    Merge request type.
    """
    metrics = graphene.Field(MergeRequestMetricsType)
    problems = graphene.List(graphene.String)

    class Meta:
        model = MergeRequest
        interfaces = (DatasourceRelayNode, WorkItem)
        connection_class = DataSourceConnection
        name = 'MergeRequest'

    def resolve_metrics(self, info, **kwargs):
        """
        Get merge request metrics.
        """
        return get_merge_request_metrcis(self)

    def resolve_problems(self, info, **kwargs):
        """
        Get merge request problems.
        """
        return get_merge_request_problems(self)

    def resolve_participants(self, info, **kwargs):
        """
        Get merge request participants.
        """
        return getattr(self, '_participants_', self.participants)

    def resolve_labels(self, info, **kwargs):
        """
        Get merge request labels.
        """
        return getattr(self, '_labels_', self.labels)

    def resolve_issues(self, info, **kwargs):
        """
        Get merge request issues.
        """
        return getattr(self, '_issues_', self.issues)

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:
        """
        Get queryset.
        """
        queryset = filter_allowed_for_user(
            queryset,
            info.context.user,
        )

        if is_field_selected(info, 'edges.node.user'):
            queryset = queryset.select_related('user')

        # TODO: condsider using graphene_django_optimizer here
        if is_field_selected(info, 'edges.node.participants'):
            from apps.users.graphql.types import UserType

            users = get_user_model().objects
            queryset = queryset.prefetch_related(Prefetch(
                'participants',
                queryset=UserType.get_queryset(users, info).all(),
                to_attr='_participants_',
            ))

        # TODO: condsider using graphene_django_optimizer here
        if is_field_selected(info, 'edges.node.labels'):
            from apps.development.graphql.types import LabelType

            queryset = queryset.prefetch_related(Prefetch(
                'labels',
                queryset=LabelType.get_queryset(Label.objects, info).all(),
                to_attr='_labels_',
            ))

        # TODO: condsider using graphene_django_optimizer here
        if is_field_selected(info, 'edges.node.issues'):
            from apps.development.graphql.types import IssueType

            queryset = queryset.prefetch_related(Prefetch(
                'issues',
                queryset=IssueType.get_queryset(Issue.objects, info).all(),
                to_attr='_issues_',
            ))

        return queryset
