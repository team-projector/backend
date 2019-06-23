from rest_framework import serializers


class UserMetricsSerializer(serializers.Serializer):
    payroll_closed = serializers.FloatField()
    payroll_opened = serializers.FloatField()
    bonus = serializers.FloatField()
    penalty = serializers.FloatField()
    issues_opened_count = serializers.IntegerField()
    issues_closed_spent = serializers.FloatField()
    issues_opened_spent = serializers.FloatField()
