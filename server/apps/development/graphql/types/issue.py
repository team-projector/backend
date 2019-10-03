# -*- coding: utf-8 -*-

import graphene
from django.contrib.auth import get_user_model
from django.db.models import Prefetch, QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.core.graphql.utils import is_field_selected
from apps.development.graphql.types.interfaces import WorkItem
from apps.development.models import Issue, Label
from apps.development.services.allowed.issues import filter_allowed_for_user
from apps.development.services.metrics.issue import get_issue_metrcis
from apps.development.services.problems.issue import get_issue_problems

from .issue_metrics import IssueMetricsType


class IssueType(BaseDjangoObjectType):
    """
    A class representing Issue model.
    """
    metrics = graphene.Field(IssueMetricsType)
    problems = graphene.List(graphene.String)

    class Meta:
        model = Issue
        filter_fields: list = []
        interfaces = (DatasourceRelayNode, WorkItem)
        connection_class = DataSourceConnection
        name = 'Issue'

    def resolve_problems(self, info, **kwargs):
        return get_issue_problems(self)

    def resolve_metrics(self, info, **kwargs):
        return get_issue_metrcis(self)

    def resolve_participants(self, info, **kwargs):
        return getattr(self, '_participants_', self.participants)

    def resolve_labels(self, info, **kwargs):
        return getattr(self, '_labels_', self.labels)

    @classmethod
    def get_queryset(
        cls,
        queryset,
        info,
    ) -> QuerySet:
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

        return queryset
