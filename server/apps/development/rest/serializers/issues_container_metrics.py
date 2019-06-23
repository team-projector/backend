from rest_framework import serializers


class IssuesContainerMetrics(serializers.Serializer):
    time_estimate = serializers.IntegerField()
    time_spent = serializers.IntegerField()
    time_remains = serializers.IntegerField()
    issues_count = serializers.IntegerField()
    issues_closed_count = serializers.IntegerField()
    issues_opened_count = serializers.IntegerField()
    efficiency = serializers.FloatField()
    payroll = serializers.FloatField()
    customer_payroll = serializers.FloatField()
