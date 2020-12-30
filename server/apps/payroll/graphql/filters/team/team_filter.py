import django_filters
from django.db.models import QuerySet

from apps.development.models import Team


class TeamFilter(django_filters.ModelChoiceFilter):
    """Team choice filter."""

    def __init__(self) -> None:
        """Initialize self."""
        super().__init__(queryset=Team.objects.all())

    def filter(  # noqa: A003, WPS125
        self,
        queryset,
        team,
    ) -> QuerySet:
        """Do filtering."""
        if not team:
            return queryset

        return queryset.filter(user__teams=team)
