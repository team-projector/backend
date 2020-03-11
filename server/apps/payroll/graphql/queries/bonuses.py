# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.payroll.graphql.filters import BonusFilterSet
from apps.payroll.graphql.types import BonusType


class BonusesQueries(graphene.ObjectType):
    """Class representing list of available fields for bonuses queries."""

    bonus = DatasourceRelayNode.Field(BonusType)
    all_bonuses = DataSourceConnectionField(
        BonusType, filterset_class=BonusFilterSet,
    )
