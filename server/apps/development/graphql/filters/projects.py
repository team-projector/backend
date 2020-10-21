import django_filters
from jnt_django_graphene_toolbox.filters import OrderingFilter, SearchFilter

from apps.development.models import Project


class ProjectsFilterSet(django_filters.FilterSet):
    """Set of filters for Milestone."""

    class Meta:
        model = Project
        fields = ("title", "state")

    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("title",))
