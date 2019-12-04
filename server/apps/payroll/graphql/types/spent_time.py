# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.interfaces import WorkItem
from apps.payroll.models import SpentTime
from apps.payroll.services.spent_time.allowed import filter_allowed_for_user


class SpentTimeType(BaseDjangoObjectType):
    """Spent Time type."""

    owner = graphene.Field(WorkItem)

    class Meta:
        model = SpentTime
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'SpentTime'

    def resolve_owner(self, info, **kwargs):  # noqa: WPS110
        """Get spent time owner: issue or merge request."""
        return self.base

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get spent times."""
        return filter_allowed_for_user(
            queryset,
            info.context.user,
        )
