from bitfield.rest.fields import BitField
from rest_framework import serializers

from apps.users.models import User
from .mixins import UserMetricsMixin


class UserSerializer(UserMetricsMixin,
                     serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()
    avatar = serializers.URLField(source='gl_avatar')
    roles = BitField()

    class Meta:
        model = User
        fields = ('id', 'name', 'login', 'hour_rate', 'avatar', 'gl_url', 'roles', 'metrics')


class UserCardSerializer(UserMetricsMixin,
                         serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()
    avatar = serializers.URLField(source='gl_avatar')
    roles = BitField()

    class Meta:
        model = User
        fields = ('id', 'name', 'avatar', 'roles', 'metrics')
