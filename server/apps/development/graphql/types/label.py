# -*- coding: utf-8 -*-

from typing import List

from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.development.models import Label


class LabelType(BaseDjangoObjectType):
    """Label type."""

    class Meta:
        model = Label
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        filter_fields: List[str] = []
        name = "Label"
