import django_filters
from jnt_django_graphene_toolbox.filters import OrderingFilter, SearchFilter
from jnt_django_graphene_toolbox.filters.strings_array import (
    StringsArrayFilter,
)

from apps.development.models import Project


class ProjectStatesFilter(StringsArrayFilter):
    """Project states filter."""

    def filter(self, queryset, states):  # noqa: A003 WPS125
        """Filter queryset by states."""
        if states:
            queryset = queryset.filter(state__in=states)
        return queryset


class ProjectsFilterSet(django_filters.FilterSet):
    """Set of filters for projects."""

    class Meta:
        model = Project
        fields = ("title",)

    state = ProjectStatesFilter()
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("title", "state"))
