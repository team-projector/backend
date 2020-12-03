import django_filters
from jnt_django_graphene_toolbox.filters import (
    EnumMultipleFilter,
    OrderingFilter,
    SearchFilter,
)

from apps.development.models import Project
from apps.development.models.choices.project_state import ProjectState


class ProjectGroupsFilterSet(django_filters.FilterSet):
    """Set of filters for project groups."""

    class Meta:
        model = Project
        fields = ("title",)

    state = EnumMultipleFilter(enum=ProjectState)
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("title", "state", "full_title"))
