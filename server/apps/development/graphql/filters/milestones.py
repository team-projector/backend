import django_filters
from jnt_django_graphene_toolbox.filters import OrderingFilter, SearchFilter

from apps.development.models.milestone import Milestone


class MilestonesFilterSet(django_filters.FilterSet):
    """Set of filters for Milestone."""

    class Meta:
        model = Milestone
        fields = ("state",)

    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("due_date",))
