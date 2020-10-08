from graphene_django import DjangoObjectType
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.development.graphql.interfaces import MilestoneOwner
from apps.development.models import ProjectGroup


class ProjectGroupType(DjangoObjectType):
    """Project Group type."""

    class Meta:
        model = ProjectGroup
        interfaces = (DatasourceRelayNode, MilestoneOwner)
        connection_class = DataSourceConnection
        name = "ProjectGroup"
