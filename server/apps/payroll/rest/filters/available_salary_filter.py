from rest_framework import filters

from apps.payroll.services.salaries import filter_available_salaries


class AvailableSalaryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return filter_available_salaries(queryset, request.user)
