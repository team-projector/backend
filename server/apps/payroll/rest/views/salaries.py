from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import mixins

from apps.core.rest.views import BaseGenericViewSet
from apps.payroll.models import Salary
from apps.payroll.rest.permissions import CanViewSalaries
from ..serializers import SalarySerializer


class SalariesViewSet(mixins.RetrieveModelMixin,
                      BaseGenericViewSet):
    permission_classes = (CanViewSalaries,)
    actions_serializers = {
        'retrieve': SalarySerializer,
    }
    queryset = Salary.objects.all()

    @cached_property
    def salary(self):
        salary = get_object_or_404(
            Salary.objects,
            pk=self.kwargs['pk']
        )
        self.check_object_permissions(
            self.request,
            salary
        )

        return salary

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(pk=self.salary.pk)
