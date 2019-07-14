from rest_framework import serializers

from apps.users.models import User
from .user_progress_metrics import UserProgressMetricsSerializer


class TeamMemberProgressMetricsSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    metrics = UserProgressMetricsSerializer(many=True)
