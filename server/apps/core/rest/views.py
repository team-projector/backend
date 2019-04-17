from typing import Dict

from rest_framework import generics, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import LinkSerializer


class BaseGenericAPIView(generics.GenericAPIView):
    serializer_classes: Dict[str, serializers.Serializer] = {}

    def get_serializer_class(self):
        return (self.serializer_classes[self.request.method]
                if self.request.method in self.serializer_classes
                else super().get_serializer_class())


class BaseGenericViewSet(viewsets.GenericViewSet):
    serializer_classes: Dict[str, serializers.Serializer] = {}

    def get_serializer_class(self):
        return self.serializer_classes[self.action] \
            if self.action in self.serializer_classes \
            else super().get_serializer_class()

    def get_update_serializer(self, request, instance=None, *args, **kwargs):
        assert self.update_serializer_class is not None, \
            f'"{self.__class__.__name__}" should include a `update_serializer_class` attribute'

        params = {
            'context': self.get_serializer_context(),
            'data': request.data,
            'partial': kwargs.pop('partial', False)
        }

        return self.update_serializer_class(instance, *args, **params)


class LinksViewMixin:
    @action(detail=False, serializer_class=LinkSerializer, pagination_class=None)
    def links(self, request, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
