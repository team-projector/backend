from rest_framework import filters

from apps.payroll.models import SpentTime


class AvailableSpentFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            id__in=SpentTime.objects.get_available(request.user)
        )
