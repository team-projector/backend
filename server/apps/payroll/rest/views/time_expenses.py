from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions

from apps.core.rest.views import BaseGenericAPIView
from apps.payroll.models import SpentTime
from apps.payroll.rest.permissions import CanViewUserMetrics
from ..serializers import TimeExpenseSerializer

User = get_user_model()


class TimeExpensesView(mixins.ListModelMixin,
                       BaseGenericAPIView):
    queryset = SpentTime.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('date',)
    permission_classes = (
        permissions.IsAuthenticated,
        CanViewUserMetrics
    )
    serializer_class = TimeExpenseSerializer

    @cached_property
    def user(self):
        user = get_object_or_404(
            User.objects,
            pk=self.kwargs['user_pk']
        )
        self.check_object_permissions(
            self.request,
            user
        )

        return user

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(user=self.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
