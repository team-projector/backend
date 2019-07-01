from rest_framework import filters

from apps.payroll.models import WorkBreak


class AvailableWorkBreakFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            id__in=WorkBreak.objects.get_available(request.user)
        )
