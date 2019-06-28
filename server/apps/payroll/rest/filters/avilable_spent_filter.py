from rest_framework import filters

from apps.payroll.services.time_spents import get_available_spent_times


class AvailableSpentFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return get_available_spent_times(request.user, queryset)
