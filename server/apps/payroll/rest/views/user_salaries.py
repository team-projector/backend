from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import mixins, permissions

from apps.core.rest.views import BaseGenericAPIView
from apps.payroll.models import Salary
from apps.payroll.rest.permissions import CanViewUserMetrics
from ..serializers import SalarySerializer

User = get_user_model()


class UserSalariesView(mixins.ListModelMixin,
                       BaseGenericAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        CanViewUserMetrics
    )
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer

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
