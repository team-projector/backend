from rest_framework import serializers


class UserProgressMetricsSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    time_estimate = serializers.IntegerField()
    time_spent = serializers.IntegerField()
    time_remains = serializers.IntegerField()
    issues_count = serializers.IntegerField()
    loading = serializers.IntegerField()
    efficiency = serializers.FloatField()
    payroll = serializers.FloatField()
    paid = serializers.FloatField()
    planned_work_hours = serializers.IntegerField()
