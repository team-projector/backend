from rest_framework import serializers

from .issues_container_metrics import IssuesContainerMetrics


class MilestoneMetricsSerializer(IssuesContainerMetrics):
    profit = serializers.IntegerField()
    budget_remains = serializers.IntegerField()
