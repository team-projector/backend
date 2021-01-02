import graphene

from apps.development.graphql.fields import AllProjectGroupsConnectionField
from apps.development.graphql.resolvers import resolve_project_groups_summary
from apps.development.graphql.types import ProjectGroupsSummaryType


class ProjectGroupsQueries(graphene.ObjectType):
    """Class represents list of fields for project groups queries."""

    all_project_groups = AllProjectGroupsConnectionField()
    project_groups_summary = graphene.Field(
        ProjectGroupsSummaryType,
        resolver=resolve_project_groups_summary,
    )
