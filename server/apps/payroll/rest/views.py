from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView, BaseGenericViewSet
from apps.core.rest.mixins.views import CreateModelMixin, UpdateModelMixin
from apps.core.utils.rest import parse_query_params
from apps.development.models import TeamMember
from apps.development.rest.permissions import IsTeamLeader
from apps.payroll.rest.permissions import CanViewUserMetrics
from .serializers import SalarySerializer, TimeExpenseSerializer, UserProgressMetricsParamsSerializer, \
    UserProgressMetricsSerializer, WorkBreakSerializer, WorkBreakCardSerializer, WorkBreakUpdateSerializer
from ..models import Salary, SpentTime, WorkBreak
from ..utils.metrics.progress import create_progress_calculator

User = get_user_model()


class UserProgressMetricsView(BaseGenericAPIView):
    permission_classes = (permissions.IsAuthenticated, CanViewUserMetrics)

    @cached_property
    def user(self):
        user = get_object_or_404(User.objects, pk=self.kwargs['user_pk'])
        self.check_object_permissions(self.request, user)

        return user

    def get(self, request, **kwargs):
        params = parse_query_params(request, UserProgressMetricsParamsSerializer)

        calculator = create_progress_calculator(self.user, params['start'], params['end'], params['group'])
        metrics = calculator.calculate()

        return Response(UserProgressMetricsSerializer(metrics, many=True).data)


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
    permission_classes = (permissions.IsAuthenticated,)

    serializer_classes = {
        'create': WorkBreakSerializer,
        'update': WorkBreakUpdateSerializer,
        'retrieve': WorkBreakSerializer,
        'destroy': WorkBreakSerializer,
    }
    update_serializer_class = WorkBreakUpdateSerializer

    queryset = WorkBreak.objects.all()

    ordering_fields = ('from_date',)
    ordering = ('from_date',)

    def get_permissions(self):
        if self.action in ['decline', 'approve', 'approving']:
            return [permissions.IsAuthenticated(), IsTeamLeader()]
        return super().get_permissions()

    @action(detail=False,
            serializer_class=WorkBreakCardSerializer)
    def approving(self, request):
        teams_ids = list(TeamMember.objects.filter(user=request.user,
                                                   roles=TeamMember.roles.leader).values_list('team', flat=True))
        users_ids = set(TeamMember.objects.filter(team__in=teams_ids).values_list('user', flat=True))
        users_ids.discard(request.user.id)

        queryset = self.get_queryset().filter(user__in=users_ids, approve_state='created')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post'],
            serializer_class=WorkBreakSerializer)
    def decline(self, request, pk=None):
        serializer = self.get_serializer_from_instance(request, approve_state='decline')
        return Response(serializer.data)

    @action(detail=True,
            methods=['post'],
            serializer_class=WorkBreakSerializer,)
    def approve(self, request, pk=None):
        serializer = self.get_serializer_from_instance(request, approve_state='approved')
        return Response(serializer.data)

    def get_serializer_from_instance(self, request, approve_state):
        instance = self.get_object()
        instance.approve_state = approve_state
        instance.approved_by = User.objects.get(id=request.user.id)
        instance.approved_at = timezone.now()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return serializer
