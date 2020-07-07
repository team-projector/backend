# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.development.graphql.interfaces import WorkItem
from apps.payroll.models import Penalty
from apps.payroll.services.salary.allowed import filter_allowed_for_user


class PenaltyType(BaseDjangoObjectType):
    """Penalty type."""

    class Meta:
        model = Penalty
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "Penalty"

    owner = graphene.Field(WorkItem)

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get salaries."""
        return filter_allowed_for_user(queryset, info.context.user)
