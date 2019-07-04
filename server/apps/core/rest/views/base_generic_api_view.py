from typing import Dict

from rest_framework import generics, serializers


class BaseGenericAPIView(generics.GenericAPIView):
    actions_serializers: Dict[str, serializers.Serializer] = {}

    def get_serializer_class(self):
        return (self.actions_serializers[self.request.method]
                if self.request.method in self.actions_serializers
                else super().get_serializer_class())
