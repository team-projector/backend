import graphene
from jnt_django_graphene_toolbox.nodes import ModelRelayNode

from apps.development.graphql.fields import AllProjectsConnectionField
from apps.development.graphql.resolvers import resolve_projects_summary
from apps.development.graphql.types import ProjectsSummaryType, ProjectType


class ProjectsQueries(graphene.ObjectType):
    """Class represents list of available fields for project queries."""

    project = ModelRelayNode.Field(ProjectType)
    all_projects = AllProjectsConnectionField()
    projects_summary = graphene.Field(
        ProjectsSummaryType,
        resolver=resolve_projects_summary,
    )
