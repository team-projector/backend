from rest_framework import filters, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericViewSet
from apps.development.models import Milestone, Project, ProjectGroup
from apps.development.rest import permissions
from apps.development.rest.filters import MilestoneActiveFilter
from apps.development.rest.serializers import MilestoneCardSerializer
from apps.development.tasks import sync_group_milestone, sync_project_milestone


class MilestonesViewset(mixins.ListModelMixin,
                        BaseGenericViewSet):
    permission_classes = (
        IsAuthenticated,
        permissions.IsProjectManager
    )

    serializer_classes = {
        'list': MilestoneCardSerializer
    }

    queryset = Milestone.objects.all()
    filter_backends = (
        filters.OrderingFilter,
        MilestoneActiveFilter
    )
    ordering = ('-due_date',)

    @action(detail=True,
            methods=['post'],
            serializer_class=MilestoneCardSerializer,
            permission_classes=(IsAuthenticated,))
    def sync(self, request, pk=None):
        milestone = self.get_object()

        if milestone.content_type.model_class() == Project:
            sync_project_milestone.delay(milestone.owner.gl_id, milestone.gl_id)
        elif milestone.content_type.model_class() == ProjectGroup:
            sync_group_milestone.delay(milestone.owner.gl_id, milestone.gl_id)

        return Response(self.get_serializer(self.get_object()).data)
