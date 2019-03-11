from bitfield.rest.fields import BitField
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from apps.users.rest.authentication import TokenAuthentication
from ..models import Token, User


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')

        if login and password:
            user = authenticate(request=self.context['request'],
                                login=login,
                                password=password)

            if not user:
                raise AuthenticationFailed(_('MESSAGE_UNABLE_TO_LOGIN_WITH_PROVIDED_CREDENTIALS'))
        else:
            raise AuthenticationFailed(_('MESSAGE_MUST_INCLUDE_LOGIN_AND_PASSWORD'))

        attrs['user'] = user
        return attrs

    class Meta:
        fields = ('login', 'pasword')


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source='key')
    type = serializers.SerializerMethodField()

    @staticmethod
    def get_type(instance):
        return TokenAuthentication.keyword

    class Meta:
        model = Token
        fields = ('token', 'type')


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.URLField(source='gl_avatar')
    roles = BitField()

    class Meta:
        model = User
        fields = ('id', 'name', 'login', 'hour_rate', 'avatar', 'gl_url', 'roles')


class UserCardSerializer(serializers.ModelSerializer):
    avatar = serializers.URLField(source='gl_avatar')
    roles = BitField()

    class Meta:
        model = User
        fields = ('id', 'name', 'avatar', 'roles')
