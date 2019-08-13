from rest_framework import mixins

from apps.core.rest.views import BaseGenericViewSet
from apps.core.rest.views.mixins import CreateModelMixin, UpdateModelMixin
from apps.payroll.models import WorkBreak
from apps.payroll.rest.serializers import (
    WorkBreakSerializer, WorkBreakUpdateSerializer
)


class WorkBreaksViewset(CreateModelMixin,
                        UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        BaseGenericViewSet):
    actions_serializers = {
        'create': WorkBreakSerializer,
        'update': WorkBreakSerializer,
        'destroy': WorkBreakSerializer,
    }
    update_serializer_class = WorkBreakUpdateSerializer

    queryset = WorkBreak.objects.all()
