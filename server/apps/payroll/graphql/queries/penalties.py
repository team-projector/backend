# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.payroll.graphql.filters import PenaltyFilterSet
from apps.payroll.graphql.types import PenaltyType


class PenaltiesQueries(graphene.ObjectType):
    """Class representing list of available fields for penalty queries."""

    penalty = DatasourceRelayNode.Field(PenaltyType)
    all_penalties = DataSourceConnectionField(
        PenaltyType, filterset_class=PenaltyFilterSet,
    )
