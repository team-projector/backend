from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from apps.core.utils.rest import parse_query_params
from apps.development.models import Team
from apps.payroll.rest.permissions import CanViewTeamMetrics, CanViewUserMetrics
from apps.payroll.services.metrics.progress.team import calculate_team_progress_metrics
from apps.payroll.services.metrics.progress.user import calculate_user_progress_metrics
from .serializers import (
    SalarySerializer, TeamMemberProgressMetricsSerializer, TeamProgressMetricsParamsSerializer,
    TimeExpenseSerializer, UserProgressMetricsParamsSerializer, UserProgressMetricsSerializer
)
from ..models import Salary, SpentTime

User = get_user_model()


class UserProgressMetricsView(BaseGenericAPIView):
    permission_classes = (permissions.IsAuthenticated, CanViewUserMetrics)

    @cached_property
    def user(self) -> User:
        user = get_object_or_404(User.objects, pk=self.kwargs['user_pk'])
        self.check_object_permissions(self.request, user)

        return user

    def get(self, request, **kwargs):
        params = parse_query_params(request, UserProgressMetricsParamsSerializer)

        metrics = calculate_user_progress_metrics(
            self.user,
            params['start'],
            params['end'],
            params['group']
        )

        return Response(UserProgressMetricsSerializer(metrics, many=True).data)


class TeamProgressMetricsView(BaseGenericAPIView):
    permission_classes = (permissions.IsAuthenticated, CanViewTeamMetrics)

    @cached_property
    def team(self) -> Team:
        team = get_object_or_404(Team.objects, pk=self.kwargs['team_pk'])
        self.check_object_permissions(self.request, team)

        return team

    def get(self, request, **kwargs):
        params = parse_query_params(request, TeamProgressMetricsParamsSerializer)

        metrics = calculate_team_progress_metrics(
            self.team,
            params['start'],
            params['end'],
            params['group']
        )

        return Response(TeamMemberProgressMetricsSerializer(metrics, many=True).data)


class UserSalariesView(mixins.ListModelMixin,
                       BaseGenericAPIView):
    permission_classes = (permissions.IsAuthenticated, CanViewUserMetrics)
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer

    @cached_property
    def user(self):
        user = get_object_or_404(User.objects, pk=self.kwargs['user_pk'])
        self.check_object_permissions(self.request, user)

        return user

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(user=self.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class TimeExpensesView(mixins.ListModelMixin,
                       BaseGenericAPIView):
    queryset = SpentTime.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('date',)
    permission_classes = (permissions.IsAuthenticated, CanViewUserMetrics)
    serializer_class = TimeExpenseSerializer

    @cached_property
    def user(self):
        user = get_object_or_404(User.objects, pk=self.kwargs['user_pk'])
        self.check_object_permissions(self.request, user)

        return user

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(user=self.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
