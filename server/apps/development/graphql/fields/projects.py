import django_filters
import graphene
from jnt_django_graphene_toolbox.fields import BaseModelConnectionField
from jnt_django_graphene_toolbox.filters import (
    EnumMultipleFilter,
    SearchFilter,
)

from apps.core.graphql.queries.filters import OrderingFilter
from apps.development.graphql.types.enums import ProjectState
from apps.development.models import Project


class ProjectsFilterSet(django_filters.FilterSet):
    """Set of filters for projects."""

    class Meta:
        model = Project
        fields = ("title",)

    state = EnumMultipleFilter(enum=ProjectState)
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("title", "state", "full_title"))


class ProjectSort(graphene.Enum):
    """Allowed sort fields."""

    TITLE_ASC = "title"  # noqa: WPS115
    TITLE_DESC = "-title"  # noqa: WPS115
    STATE_ASC = "state"  # noqa: WPS115
    STATE_DESC = "-state"  # noqa: WPS115
    FULL_TITLE_ASC = "full_title"  # noqa: WPS115
    FULL_TITLE_DESC = "-full_title"  # noqa: WPS115


class ProjectsConnectionField(BaseModelConnectionField):
    """Handler for projects collections."""

    filterset_class = ProjectsFilterSet
    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.ProjectType",
            order_by=graphene.Argument(graphene.List(ProjectSort)),
            q=graphene.String(),
            title=graphene.String(),
            state=graphene.Argument(graphene.List(ProjectState)),
        )
