from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from apps.core.rest.views import BaseGenericViewSet, LinksViewMixin
from apps.payroll.rest.permissions import CanViewEmbeddedUserMetrics
from apps.users.models import User
from apps.users.rest.serializers import UserSerializer


class UsersViewset(LinksViewMixin,
                   mixins.RetrieveModelMixin,
                   BaseGenericViewSet):
    permission_classes = (
        IsAuthenticated,
        CanViewEmbeddedUserMetrics
    )

    queryset = User.objects.filter(is_active=True)
    actions_serializers = {
        'retrieve': UserSerializer
    }
