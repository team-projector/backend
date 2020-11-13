import django_filters
from jnt_django_graphene_toolbox.filters import OrderingFilter

from apps.development.models import Issue


class TicketIssuesFilterSet(django_filters.FilterSet):
    """Set of filters for Issues."""

    class Meta:
        model = Issue
        fields = (
            "state",
            "user",
        )

    order_by = OrderingFilter(fields=("user", "state"))
