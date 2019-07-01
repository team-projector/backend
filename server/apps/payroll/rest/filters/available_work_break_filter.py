from rest_framework import filters

from apps.payroll.services.work_break import filter_available_work_breaks


class AvailableWorkBreakFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return filter_available_work_breaks(queryset, request.user)
