from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from apps.users.rest.serializers import LoginSerializer, TokenSerializer
from apps.users.services.token import create_user_token


class LoginView(BaseGenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        token = create_user_token(user)

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response(TokenSerializer(
            token,
            context=self.get_serializer_context()
        ).data)
