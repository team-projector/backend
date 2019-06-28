from rest_framework import serializers


class IssuesSummarySerializer(serializers.Serializer):
    issues_count = serializers.IntegerField()
    time_spent = serializers.IntegerField()
    problems_count = serializers.IntegerField()
