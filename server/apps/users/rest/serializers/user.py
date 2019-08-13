from bitfield.rest.fields import BitField
from rest_framework import serializers

from apps.payroll.services.metrics.user import UserMetricsProvider
from apps.users.models import User
from .user_metrics import UserMetricsSerializer


class MetricsMixin(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()

    def get_metrics(self, instance):
        query_params = self.context['request'].query_params
        show_metrics = query_params.get('metrics', 'false') != 'false'
        if not show_metrics:
            return None

        provider = UserMetricsProvider()
        metrics = provider.get_metrics(instance)

        return UserMetricsSerializer(metrics).data


class UserCardSerializer(MetricsMixin,
                         serializers.ModelSerializer):
    avatar = serializers.URLField(source='gl_avatar')
    roles = BitField()

    class Meta:
        model = User
        fields = ('id', 'name', 'avatar', 'roles', 'metrics')
