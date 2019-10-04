# -*- coding: utf-8 -*-

from graphene_django import DjangoObjectType

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.development.graphql.types.interfaces import MilestoneOwner
from apps.development.models import ProjectGroup


class ProjectGroupType(DjangoObjectType):
    """
    Project Group type.
    """
    class Meta:
        model = ProjectGroup
        interfaces = (DatasourceRelayNode, MilestoneOwner)
        connection_class = DataSourceConnection
        name = 'ProjectGroup'
