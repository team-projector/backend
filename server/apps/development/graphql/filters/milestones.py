import django_filters
from django.db.models import QuerySet

from apps.development.models import Milestone


class ActiveFilter(django_filters.BooleanFilter):
    def filter(self, queryset, value) -> QuerySet:
        if value is None:
            return queryset

        return queryset.filter(
            state=Milestone.STATE.active if value else Milestone.STATE.closed
        )


class MilestonesFilterSet(django_filters.FilterSet):
    active = ActiveFilter()
