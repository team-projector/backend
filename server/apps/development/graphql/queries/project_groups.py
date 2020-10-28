import graphene
from jnt_django_graphene_toolbox.connection_fields import (
    DataSourceConnectionField,
)

from apps.development.graphql.filters import ProjectGroupsFilterSet
from apps.development.graphql.resolvers import resolve_project_groups_summary
from apps.development.graphql.types import (
    ProjectGroupsSummaryType,
    ProjectGroupType,
)


class ProjectGroupsQueries(graphene.ObjectType):
    """Class represents list of fields for project groups queries."""

    all_project_groups = DataSourceConnectionField(
        ProjectGroupType,
        filterset_class=ProjectGroupsFilterSet,
    )
    project_groups_summary = graphene.Field(
        ProjectGroupsSummaryType,
        resolver=resolve_project_groups_summary,
    )
