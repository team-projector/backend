from rest_framework import serializers


class TeamMetricsSerializer(serializers.Serializer):
    issues_count = serializers.IntegerField()
    problems_count = serializers.IntegerField()
