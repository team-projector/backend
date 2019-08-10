from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions
from rest_framework.decorators import action

from apps.core.rest.views import BaseGenericViewSet
from apps.core.rest.views.mixins import CreateModelMixin, UpdateModelMixin
from apps.development.models import TeamMember
from apps.payroll.db.mixins.approved import CREATED
from apps.payroll.models import WorkBreak
from apps.payroll.rest.permissions import CanApproveDeclineWorkbreaks
from apps.payroll.rest.serializers import (
    WorkBreakCardSerializer, WorkBreakSerializer, WorkBreakUpdateSerializer
)
from ..filters import TeamFilter, AvailableWorkBreakFilter

User = get_user_model()


class WorkBreaksViewset(mixins.ListModelMixin,
                        CreateModelMixin,
                        UpdateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        BaseGenericViewSet):
    actions_serializers = {
        'list': WorkBreakCardSerializer,
        'create': WorkBreakSerializer,
        'update': WorkBreakSerializer,
        'retrieve': WorkBreakSerializer,
        'destroy': WorkBreakSerializer,
    }
    update_serializer_class = WorkBreakUpdateSerializer

    filter_backends = (
        DjangoFilterBackend,
        AvailableWorkBreakFilter,
        TeamFilter
    )
    filterset_fields = ('user',)

    queryset = WorkBreak.objects.all()

    ordering_fields = ('from_date',)
    ordering = ('from_date',)

    @action(detail=False,
            serializer_class=WorkBreakCardSerializer,
            permission_classes=(
                permissions.IsAuthenticated,
                CanApproveDeclineWorkbreaks
            ))
    def approving(self, request):
        teams = TeamMember.objects.filter(
            user=request.user,
            roles=TeamMember.roles.leader
        ).values_list(
            'team',
            flat=True
        )

        subquery = User.objects.filter(
            teams__in=teams,
            id=OuterRef('user_id')
        )

        queryset = self.get_queryset().annotate(
            user_is_team_member=Exists(subquery)
        ).filter(
            user_is_team_member=True,
            approve_state=CREATED
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)
