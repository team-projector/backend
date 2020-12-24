import django_filters
from jnt_django_graphene_toolbox.filters import (
    EnumMultipleFilter,
    SearchFilter,
)

from apps.core.graphql.queries.filters import OrderingFilter
from apps.development.models import Project
from apps.development.models.choices.project_state import ProjectState


class ProjectsFilterSet(django_filters.FilterSet):
    """Set of filters for projects."""

    class Meta:
        model = Project
        fields = ("title",)

    state = EnumMultipleFilter(enum=ProjectState)
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("title", "state", "full_title"))
