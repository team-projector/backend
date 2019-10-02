# -*- coding: utf-8 -*-

import graphene
from django.contrib.auth import get_user_model
from django.db.models import Prefetch, QuerySet

from apps.core import graphql
from apps.development import models as development_models
from apps.development import services as development_services
from apps.development.graphql.types.interfaces import WorkItem

from .merge_request_metrics import MergeRequestMetricsType


class MergeRequestType(graphql.BaseDjangoObjectType):
    metrics = graphene.Field(MergeRequestMetricsType)
    problems = graphene.List(graphene.String)

    class Meta:
        model = development_models.MergeRequest
        interfaces = (graphql.DatasourceRelayNode, WorkItem)
        connection_class = graphql.DataSourceConnection
        name = 'MergeRequest'

    def resolve_metrics(self, info, **kwargs):
        return development_services.get_merge_request_metrcis(self)

    def resolve_problems(self, info, **kwargs):
        return development_services.get_merge_request_problems(self)

    def resolve_participants(self, info, **kwargs):
        return getattr(self, '_participants_', self.participants)

    def resolve_labels(self, info, **kwargs):
        return getattr(self, '_labels_', self.labels)

    def resolve_issues(self, info, **kwargs):
        return getattr(self, '_issues_', self.issues)

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:
        queryset = development_services.filter_allowed_for_user(
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
                queryset=LabelType.get_queryset(
                    development_models.Label.objects, info,
                ).all(),
                to_attr='_labels_',
            ))

        # TODO: condsider using graphene_django_optimizer here
        if graphql.is_field_selected(info, 'edges.node.issues'):
            from apps.development.graphql.types import IssueType

            queryset = queryset.prefetch_related(Prefetch(
                'issues',
                queryset=IssueType.get_queryset(
                    development_models.Issue.objects, info,
                ).all(),
                to_attr='_issues_',
            ))

        return queryset
