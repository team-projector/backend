from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from apps.core.rest.views import BaseGenericViewSet
from apps.development.models import Issue, Milestone
from apps.development.rest import permissions
from apps.development.rest.serializers import IssueCardSerializer


class MilestoneIssuesViewset(mixins.ListModelMixin,
                             BaseGenericViewSet):
    permission_classes = (
        IsAuthenticated,
        permissions.IsProjectManager
    )

    serializer_classes = {
        'list': IssueCardSerializer
    }

    queryset = Issue.objects.all()

    @cached_property
    def milestone(self):
        return get_object_or_404(
            Milestone.objects,
            pk=self.kwargs['milestone_pk']
        )

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(
            milestone=self.milestone
        ))


class MilestoneIssuesOrphanViewset(mixins.ListModelMixin,
                                   BaseGenericViewSet):
    permission_classes = (
        IsAuthenticated,
        permissions.IsProjectManager
    )

    serializer_classes = {
        'list': IssueCardSerializer
    }

    queryset = Issue.objects.all()

    @cached_property
    def milestone(self):
        return get_object_or_404(
            Milestone.objects,
            pk=self.kwargs['milestone_pk']
        )

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(
            milestone=self.milestone,
            feature__isnull=True
        ))
