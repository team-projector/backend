from rest_framework import serializers

from apps.users.models import User


class MetricsParamsSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    start = serializers.DateField()
    end = serializers.DateField()
    group = serializers.CharField()


class MetricSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    time_spent = serializers.IntegerField()
    time_estimate = serializers.IntegerField()
    efficiency = serializers.FloatField()
    earnings = serializers.IntegerField()
