# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.payroll.services.metrics.user import UserMetricsProvider
from apps.users.models import User
from apps.users.services.problems.user import get_user_problems

from .user_metrics import UserMetricsType


class UserType(BaseDjangoObjectType):
    metrics = graphene.Field(UserMetricsType)
    problems = graphene.List(graphene.String)

    class Meta:
        model = User
        exclude_fields = ('password',)
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'User'

    def resolve_metrics(self, info, **kwargs):
        provider = UserMetricsProvider()
        return provider.get_metrics(self)

    def resolve_problems(self, info, **kwargs):
        return get_user_problems(self)

    @classmethod
    def get_queryset(cls,
                     queryset: QuerySet,
                     info) -> QuerySet:
        # TODO fix it (team members case)
        if issubclass(queryset.model, User):
            queryset = queryset.filter(is_active=True)

        return queryset
