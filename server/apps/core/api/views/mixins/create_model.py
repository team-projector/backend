from rest_framework import status
from rest_framework.response import Response


class CreateModelMixin:
    def create(self, request, *args, **kwargs):
        update_serializer = self.get_update_serializer(request)
        update_serializer.is_valid(raise_exception=True)

        instance = self.perform_create(update_serializer)

        response_serializer = self.get_serializer(instance)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        return serializer.save()
