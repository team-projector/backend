from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from apps.core.rest.views import BaseGenericViewSet
from apps.development.models import Feature, Issue
from apps.development.rest import permissions
from apps.development.rest.serializers import IssueCardSerializer


class FeatureIssuesViewset(mixins.ListModelMixin,
                           BaseGenericViewSet):
    permission_classes = (
        IsAuthenticated,
        permissions.IsProjectManager
    )

    actions_serializers = {
        'list': IssueCardSerializer
    }

    queryset = Issue.objects.all()

    @cached_property
    def feature(self):
        return get_object_or_404(
            Feature.objects,
            pk=self.kwargs['feature_pk']
        )

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(
            feature=self.feature
        ))
