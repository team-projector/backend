from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from apps.users.rest.serializers import UserSerializer


class MeUserView(BaseGenericAPIView):
    serializer_class = UserSerializer

    def get(self, request):
        return Response(self.get_serializer(request.user).data)
