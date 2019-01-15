from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.utils.token import create_user_token
from .serializers import LoginSerializer, TokenSerializer


class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        token = create_user_token(user)

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response(TokenSerializer(token, context=self.get_serializer_context()).data)


class LogoutView(APIView):
    def post(self, request):
        request.auth.marked_for_delete = timezone.now()
        request.auth.save()

        return Response()
