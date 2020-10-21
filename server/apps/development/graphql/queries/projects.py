import graphene
from jnt_django_graphene_toolbox.connection_fields import (
    DataSourceConnectionField,
)
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.development.graphql.filters import ProjectsFilterSet
from apps.development.graphql.types import ProjectType


class ProjectsQueries(graphene.ObjectType):
    """Class represents list of available fields for project queries."""

    project = DatasourceRelayNode.Field(ProjectType)
    all_projects = DataSourceConnectionField(
        ProjectType,
        filterset_class=ProjectsFilterSet,
    )
