from typing import Dict

from django.db.models import QuerySet
from rest_framework import serializers, viewsets


class BaseGenericViewSet(viewsets.GenericViewSet):
    actions_serializers: Dict[str, serializers.Serializer] = {}

    def get_serializer_class(self):
        return self.actions_serializers[self.action] \
            if self.action in self.actions_serializers \
            else super().get_serializer_class()

    def get_update_serializer(self, request, instance=None, *args, **kwargs):
        msg = f'"{self.__class__.__name__}" should include a ' \
            f'`update_serializer_class` attribute '

        assert self.update_serializer_class is not None, msg

        params = {
            'context': self.get_serializer_context(),
            'data': request.data,
            'partial': kwargs.pop('partial', False)
        }

        return self.update_serializer_class(instance, *args, **params)

    def get_filtered_queryset(self) -> QuerySet:
        return self.filter_queryset(self.get_queryset())
