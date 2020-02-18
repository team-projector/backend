# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.interfaces import WorkItem
from apps.payroll.models import Penalty
from apps.payroll.services.salary.allowed import filter_allowed_for_user


class PenaltyType(BaseDjangoObjectType):
    """Penalty type."""

    owner = graphene.Field(WorkItem)

    class Meta:
        model = Penalty
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "Penalty"

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get salaries."""
        return filter_allowed_for_user(
            queryset,
            info.context.user,
        )
