from rest_framework.permissions import IsAuthenticated

from apps.core.rest.mixins.views import CreateModelMixin, UpdateModelMixin
from apps.core.rest.views import BaseGenericViewSet
from apps.development.models import Feature
from apps.development.rest import permissions
from apps.development.rest.serializers import FeatureSerializer
from apps.development.rest.serializers.feature import FeatureUpdateSerializer


class FeaturesViewset(CreateModelMixin,
                      UpdateModelMixin,
                      BaseGenericViewSet):
    permission_classes = (
        IsAuthenticated,
        permissions.IsProjectManager
    )

    actions_serializers = {
        'create': FeatureSerializer,
        'update': FeatureSerializer,
        'partial_update': FeatureSerializer,
    }
    update_serializer_class = FeatureUpdateSerializer

    queryset = Feature.objects.all()
