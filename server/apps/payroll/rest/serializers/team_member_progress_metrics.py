from rest_framework import serializers

from .user_progress_metrics import UserProgressMetricsSerializer


class TeamMemberProgressMetricsSerializer(serializers.Serializer):
    user = serializers.IntegerField()
    metrics = UserProgressMetricsSerializer(many=True)
