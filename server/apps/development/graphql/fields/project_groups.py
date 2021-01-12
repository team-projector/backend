import django_filters
import graphene
from jnt_django_graphene_toolbox.fields import BaseModelConnectionField
from jnt_django_graphene_toolbox.filters import (
    EnumMultipleFilter,
    SearchFilter,
    SortHandler,
)

from apps.development.graphql.types.enums import ProjectState
from apps.development.models import ProjectGroup


class ProjectGroupSort(graphene.Enum):
    """Allowed sort fields."""

    TITLE_ASC = "title"  # noqa: WPS115
    TITLE_DESC = "-title"  # noqa: WPS115
    STATE_ASC = "state"  # noqa: WPS115
    STATE_DESC = "-state"  # noqa: WPS115
    FULL_TITLE_ASC = "full_title"  # noqa: WPS115
    FULL_TITLE_DESC = "-full_title"  # noqa: WPS115


class ProjectGroupsFilterSet(django_filters.FilterSet):
    """Set of filters for project groups."""

    class Meta:
        model = ProjectGroup
        fields = "__all__"

    state = EnumMultipleFilter(enum=ProjectState)
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = SortHandler(ProjectGroupSort)


class ProjectGroupsConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    filterset_class = ProjectGroupsFilterSet
    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.ProjectGroupType",
            order_by=graphene.Argument(graphene.List(ProjectGroupSort)),
            title=graphene.String(),
            q=graphene.String(),
            state=graphene.Argument(graphene.List(ProjectState)),
        )
