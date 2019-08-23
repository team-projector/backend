from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.rest.serializers import LinkSerializer


class LinksViewMixin:
    @action(detail=False,
            serializer_class=LinkSerializer,
            pagination_class=None)
    def links(self, request, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
