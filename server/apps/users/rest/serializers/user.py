from typing import Iterable

from bitfield.rest.fields import BitField
from django.utils.functional import cached_property
from rest_framework import serializers

from apps.payroll.services.metrics.user import UserMetricsProvider
from apps.users.models import User
from apps.users.services.problems.users import get_user_problems
from .user_metrics import UserMetricsSerializer


class MetricsMixin(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()

    def get_metrics(self, instance):
        query_params = self.context['request'].query_params
        show_metrics = query_params.get('metrics', 'false') != 'false'
        if not show_metrics:
            return None

        return UserMetricsSerializer(self.user_metrics).data

    @cached_property
    def user_metrics(self):
        provider = UserMetricsProvider()
        return provider.get_metrics(self.instance)


class ProblemsMixin(serializers.ModelSerializer):
    problems = serializers.SerializerMethodField()

    def get_problems(self, instance: User) -> Iterable[str]:
        return get_user_problems(instance)


class UserSerializer(MetricsMixin,
                     ProblemsMixin,
                     serializers.ModelSerializer):
    avatar = serializers.URLField(source='gl_avatar')
    roles = BitField()

    class Meta:
        model = User
        fields = (
            'id', 'name', 'login', 'hour_rate', 'avatar', 'gl_url', 'roles',
            'metrics', 'problems'
        )


class UserCardSerializer(MetricsMixin,
                         ProblemsMixin,
                         serializers.ModelSerializer):
    avatar = serializers.URLField(source='gl_avatar')
    roles = BitField()

    class Meta:
        model = User
        fields = ('id', 'name', 'avatar', 'roles', 'metrics', 'problems')
