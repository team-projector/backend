import django_filters
import graphene
from jnt_django_graphene_toolbox.filters import (
    EnumMultipleFilter,
    SearchFilter,
)

from apps.core.graphql.fields import BaseModelConnectionField
from apps.core.graphql.queries.filters import OrderingFilter
from apps.development.models import ProjectGroup
from apps.development.models.choices.project_state import ProjectState


class ProjectGroupsFilterSet(django_filters.FilterSet):
    """Set of filters for project groups."""

    class Meta:
        model = ProjectGroup
        fields = "__all__"

    state = EnumMultipleFilter(enum=ProjectState)
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("title", "state", "full_title"))


class ProjectGroupsConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    filterset_class = ProjectGroupsFilterSet
    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.ProjectGroupType",
            order_by=graphene.String(),
            title=graphene.String(),
            q=graphene.String(),
            state=graphene.Argument(
                graphene.List(graphene.Enum.from_enum(ProjectState)),
            ),
        )