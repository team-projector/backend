from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import filters, mixins

from apps.core.rest.views import BaseGenericViewSet
from apps.payroll.models import Salary, SpentTime
from apps.payroll.rest.permissions import CanViewSalaries
from ..serializers import TimeExpenseSerializer


class SalariesTimeExpensesViewSet(mixins.ListModelMixin,
                                  BaseGenericViewSet):
    permission_classes = (CanViewSalaries,)
    serializer_classes = {
        'list': TimeExpenseSerializer,
    }
    queryset = SpentTime.objects.all()
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('date',)

    @cached_property
    def salary(self):
        salary = get_object_or_404(
            Salary.objects,
            pk=self.kwargs['salary_pk']
        )
        self.check_object_permissions(
            self.request,
            salary
        )

        return salary

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(salary=self.salary)
