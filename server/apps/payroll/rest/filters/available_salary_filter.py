from rest_framework import filters

from apps.payroll.models import Salary


class AvailableSalaryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            id__in=Salary.objects.get_available(request.user)
        )
