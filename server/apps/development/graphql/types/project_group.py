# -*- coding: utf-8 -*-

from graphene_django import DjangoObjectType

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.development.models import ProjectGroup
from apps.development.graphql.types.interfaces import MilestoneOwner


class ProjectGroupType(DjangoObjectType):
    class Meta:
        model = ProjectGroup
        interfaces = (DatasourceRelayNode, MilestoneOwner)
        connection_class = DataSourceConnection
        name = 'ProjectGroup'
