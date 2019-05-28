from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from django.test.utils import CaptureQueriesContext
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters

from apps.core.rest.mixins.views import CreateModelMixin, UpdateModelMixin
from apps.core.rest.views import BaseGenericAPIView, BaseGenericViewSet
from apps.core.utils.rest import parse_query_params
from apps.development.models import Team, TeamMember
from apps.payroll.db.mixins import CREATED
from apps.payroll.models import WorkBreak
from apps.payroll.rest.permissions import (
    CanApproveDeclineWorkbreaks, CanManageWorkbreaks, CanViewTeamMetrics, CanViewUserMetrics, CanViewSalaries)
from apps.payroll.services.metrics.progress.team import calculate_team_progress_metrics
from apps.payroll.services.metrics.progress.user import calculate_user_progress_metrics
from .serializers import (SalarySerializer, TeamMemberProgressMetricsSerializer, TeamProgressMetricsParamsSerializer,
                          TimeExpenseSerializer, UserProgressMetricsParamsSerializer, UserProgressMetricsSerializer,
                          WorkBreakApproveSerializer, WorkBreakCardSerializer, WorkBreakDeclineSerializer,
                          WorkBreakSerializer, WorkBreakUpdateSerializer)
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


class UserWorkBreaksView(mixins.ListModelMixin,
                         BaseGenericAPIView):
    queryset = WorkBreak.objects.all()
    permission_classes = (permissions.IsAuthenticated, CanViewUserMetrics)
    serializer_class = WorkBreakCardSerializer

    @cached_property
    def user(self):
        user = get_object_or_404(User.objects, pk=self.kwargs['user_pk'])
        self.check_object_permissions(self.request, user)
        return user

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(user=self.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WorkBreaksViewset(mixins.ListModelMixin,
                        CreateModelMixin,
                        UpdateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        BaseGenericViewSet):
    permission_classes = (permissions.IsAuthenticated, CanManageWorkbreaks)

    serializer_classes = {
        'create': WorkBreakSerializer,
        'update': WorkBreakSerializer,
        'retrieve': WorkBreakSerializer,
        'destroy': WorkBreakSerializer,
    }
    update_serializer_class = WorkBreakUpdateSerializer

    queryset = WorkBreak.objects.all()

    ordering_fields = ('from_date',)
    ordering = ('from_date',)

    @action(detail=False,
            serializer_class=WorkBreakCardSerializer,
            permission_classes=(permissions.IsAuthenticated, CanApproveDeclineWorkbreaks))
    def approving(self, request):
        teams = TeamMember.objects.filter(user=request.user,
                                          roles=TeamMember.roles.leader).values_list('team', flat=True)
        subquery = User.objects.filter(team_members__team__in=teams,
                                       team_members__roles=TeamMember.roles.developer,
                                       id=OuterRef('user_id'))

        queryset = self.get_queryset().annotate(user_is_team_member=Exists(subquery)).filter(
            user_is_team_member=True,
            approve_state=CREATED
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post'],
            serializer_class=WorkBreakDeclineSerializer,
            permission_classes=(permissions.IsAuthenticated, CanApproveDeclineWorkbreaks))
    def decline(self, request, pk=None):
        instance = self.get_object()

        serializer = self.get_serializer(instance,
                                         context=self.get_serializer_context(),
                                         data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(WorkBreakSerializer(instance, context=self.get_serializer_context()).data)

    @action(detail=True,
            methods=['post'],
            serializer_class=WorkBreakApproveSerializer,
            permission_classes=(permissions.IsAuthenticated, CanApproveDeclineWorkbreaks))
    def approve(self, request, pk=None):
        instance = self.get_object()

        serializer = self.get_serializer(instance,
                                         context=self.get_serializer_context(),
                                         data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(WorkBreakSerializer(instance, context=self.get_serializer_context()).data)


class SalariesViewSet(mixins.RetrieveModelMixin,
                      BaseGenericViewSet):
    permission_classes = (CanViewSalaries,)
    serializer_classes = {
        'retrieve': SalarySerializer,
    }
    queryset = Salary.objects.all()

    @cached_property
    def salary(self):
        salary = get_object_or_404(Salary.objects, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, salary)

        return salary

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(pk=self.salary.pk)


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
        salary = get_object_or_404(Salary.objects, pk=self.kwargs['salary_pk'])
        self.check_object_permissions(self.request, salary)

        return salary

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(salary=self.salary)
