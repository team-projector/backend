from django.utils import timezone
from rest_framework import mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.rest.views import BaseGenericAPIView, BaseGenericViewSet, LinksViewMixin
from apps.payroll.rest.permissions import CanViewEmbeddedUserMetrics
from apps.users.models import User
from apps.users.utils.token import create_user_token
from .serializers import LoginSerializer, TokenSerializer, UserSerializer


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

        return Response(TokenSerializer(token, context=self.get_serializer_context()).data)


class LogoutView(APIView):
    def post(self, request):
        request.auth.delete()

        return Response()


class MeUserView(BaseGenericAPIView):
    serializer_class = UserSerializer

    def get(self, request):
        return Response(self.get_serializer(request.user).data)


class UsersViewset(LinksViewMixin,
                   mixins.RetrieveModelMixin,
                   BaseGenericViewSet):
    permission_classes = (IsAuthenticated, CanViewEmbeddedUserMetrics)

    queryset = User.objects.filter(is_active=True)
    serializer_classes = {
        'retrieve': UserSerializer
    }
