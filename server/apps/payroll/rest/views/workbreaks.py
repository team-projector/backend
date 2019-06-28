from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django.utils import timezone
from rest_framework import mixins, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.rest.mixins.views import CreateModelMixin, UpdateModelMixin
from apps.core.rest.views import BaseGenericViewSet
from apps.development.models import TeamMember
from apps.payroll.db.mixins.approved import APPROVED, CREATED, DECLINED
from apps.payroll.models import WorkBreak
from apps.payroll.rest.permissions import (
    CanApproveDeclineWorkbreaks, CanManageWorkbreaks
)
from apps.payroll.rest.serializers import (
    WorkBreakCardSerializer, WorkBreakSerializer, WorkBreakUpdateSerializer
)

User = get_user_model()


class WorkBreakApproveSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        instance.approve_state = APPROVED
        instance.approved_by = self.context['request'].user
        instance.approved_at = timezone.now()
        instance.save()

        return instance


class WorkBreakDeclineSerializer(serializers.Serializer):
    decline_reason = serializers.CharField(required=True, allow_null=False)

    def update(self, instance, validated_data):
        instance.approve_state = DECLINED
        instance.approved_by = self.context['request'].user
        instance.approved_at = timezone.now()
        instance.decline_reason = validated_data.get(
            'decline_reason',
            instance.decline_reason
        )
        instance.save()

        return instance


class WorkBreaksViewset(mixins.ListModelMixin,
                        CreateModelMixin,
                        UpdateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        BaseGenericViewSet):
    permission_classes = (
        permissions.IsAuthenticated,
        CanManageWorkbreaks
    )

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

    @action(detail=True,
            methods=['post'],
            serializer_class=WorkBreakDeclineSerializer,
            permission_classes=(
                permissions.IsAuthenticated,
                CanApproveDeclineWorkbreaks
            ))
    def decline(self, request, pk=None):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            context=self.get_serializer_context(),
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(WorkBreakSerializer(
            instance,
            context=self.get_serializer_context()
        ).data)

    @action(detail=True,
            methods=['post'],
            serializer_class=WorkBreakApproveSerializer,
            permission_classes=(
                permissions.IsAuthenticated,
                CanApproveDeclineWorkbreaks
            ))
    def approve(self, request, pk=None):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            context=self.get_serializer_context(),
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(WorkBreakSerializer(
            instance,
            context=self.get_serializer_context()
        ).data)
