from rest_framework import serializers


class IssueMetricsSerializer(serializers.Serializer):
    remains = serializers.IntegerField()
    efficiency = serializers.FloatField()
    payroll = serializers.FloatField()
    paid = serializers.FloatField()
