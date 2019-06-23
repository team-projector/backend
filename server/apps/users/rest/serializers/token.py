from rest_framework import serializers

from apps.users.models import Token
from apps.users.rest.authentication import TokenAuthentication


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source='key')
    type = serializers.SerializerMethodField()

    @staticmethod
    def get_type(instance):
        return TokenAuthentication.keyword

    class Meta:
        model = Token
        fields = ('token', 'type')
