# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet

from apps.core.graphql import get_fields_from_info
from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.users.graphql.types.user_metrics import UserMetricsType
from apps.users.models import User
from apps.users.services.user.metrics.main import UserMetricsProvider
from apps.users.services.user.problems import get_user_problems


class UserType(BaseDjangoObjectType):
    """User type."""

    class Meta:
        model = User
        exclude = ("password",)
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "User"

    metrics = graphene.Field(UserMetricsType)
    problems = graphene.List(graphene.String)

    @classmethod
    def get_queryset(
        cls, queryset: QuerySet, info,  # noqa: WPS110
    ) -> QuerySet:
        """Get queryset."""
        # TODO fix it (team members case)
        if issubclass(queryset.model, User):
            queryset = queryset.filter(is_active=True)

        return queryset

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get user metrics."""
        provider = UserMetricsProvider(get_fields_from_info(info))
        return provider.get_metrics(self)

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get user problems."""
        return get_user_problems(self)
