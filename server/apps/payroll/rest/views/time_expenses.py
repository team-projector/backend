from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, filters

from apps.core.rest.views import BaseGenericAPIView
from apps.payroll.models import SpentTime
from ..filters import TeamFilter, AvailableSpentFilter
from ..serializers import TimeExpenseSerializer


class TimeExpensesView(mixins.ListModelMixin,
                       BaseGenericAPIView):
    queryset = SpentTime.objects.all()
    filter_backends = (
        DjangoFilterBackend,
        TeamFilter,
        filters.OrderingFilter,
        AvailableSpentFilter
    )
    filterset_fields = ('date', 'user', 'salary')
    ordering_fields = ('date',)

    serializer_class = TimeExpenseSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
