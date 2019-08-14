from rest_framework import filters, mixins
from rest_framework.permissions import IsAuthenticated

from apps.core.rest.views import BaseGenericViewSet
from apps.development.models import Milestone
from apps.development.rest import permissions
from apps.development.rest.filters import MilestoneActiveFilter
from apps.development.rest.serializers import MilestoneCardSerializer


class MilestonesViewset(mixins.ListModelMixin,
                        BaseGenericViewSet):
    permission_classes = (
        IsAuthenticated,
        permissions.IsProjectManager
    )

    actions_serializers = {
        'list': MilestoneCardSerializer,
    }

    queryset = Milestone.objects.all()
    filter_backends = (
        filters.OrderingFilter,
        MilestoneActiveFilter
    )
    ordering = ('-due_date',)
