from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')

        if login and password:
            user = authenticate(
                request=self.context['request'],
                login=login,
                password=password
            )

            if not user:
                raise AuthenticationFailed(_('MSG_UNABLE_TO_LOGIN_WITH_PROVIDED_CREDENTIALS'))
        else:
            raise AuthenticationFailed(_('MSG_MUST_INCLUDE_LOGIN_AND_PASSWORD'))

        attrs['user'] = user
        return attrs

    class Meta:
        fields = ('login', 'pasword')
