# -*- coding: utf-8 -*-

from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.payroll.models import WorkBreak
from apps.payroll.services.allowed.work_break import filter_allowed_for_user


class WorkBreakType(BaseDjangoObjectType):
    """
    Work break type.
    """
    class Meta:
        model = WorkBreak
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'WorkBreak'

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:
        """
        Get work breaks.
        """
        return filter_allowed_for_user(
            queryset,
            info.context.user,
        )
