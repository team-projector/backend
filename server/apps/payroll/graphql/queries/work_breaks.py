# -*- coding: utf-8 -*-

import graphene
from jnt_django_graphene_toolbox.connection_fields import (
    DataSourceConnectionField,
)
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.payroll.graphql.filters import WorkBreakFilterSet
from apps.payroll.graphql.types import WorkBreakType


class WorkBreaksQueries(graphene.ObjectType):
    """Class representing list of available fields for work break queries."""

    work_break = DatasourceRelayNode.Field(WorkBreakType)
    all_work_breaks = DataSourceConnectionField(
        WorkBreakType,
        filterset_class=WorkBreakFilterSet,
    )
