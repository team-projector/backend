from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins

from apps.core.rest.views import BaseGenericViewSet
from apps.payroll.models import Salary
from ..filters import TeamFilter, AvailableSalaryFilter
from ..serializers import SalarySerializer


class SalariesViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      BaseGenericViewSet):
    actions_serializers = {
        'retrieve': SalarySerializer,
        'list': SalarySerializer
    }
    queryset = Salary.objects.all()
    filter_backends = (
        DjangoFilterBackend,
        AvailableSalaryFilter,
        TeamFilter
    )
    filterset_fields = ('user',)
