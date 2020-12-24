import django_filters

from apps.core.graphql.queries.filters import OrderingFilter
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
