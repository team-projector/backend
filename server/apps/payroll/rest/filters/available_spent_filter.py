from rest_framework import filters

from apps.payroll.services.time_spents import filter_available_spent_times


class AvailableSpentFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return filter_available_spent_times(queryset, request.user)
