from rest_framework import serializers

from apps.core.utils.objects import dict2obj
from apps.development.models import Team
from apps.development.rest.serializers.team_metrics import TeamMetricsSerializer
from apps.development.services.issues.problems import (
    filter_issues_problems, annotate_issues_problems
)
from .team_member import TeamMemberCardSerializer


class TeamMetricsMixin(serializers.Serializer):
    metrics = serializers.SerializerMethodField()

    def get_metrics(self, instance: Team):
        metrics = {
            'issues_count': instance.issues.count(),
            'problems_count': self.get_problems_count(instance)
        }

        return TeamMetricsSerializer(dict2obj(metrics)).data

    def get_problems_count(self, team):
        queryset = team.issues
        queryset = annotate_issues_problems(queryset)
        queryset = filter_issues_problems(queryset)

        return queryset.count()


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'title')


class TeamCardSerializer(TeamMetricsMixin, serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    members = TeamMemberCardSerializer(many=True, source='teammember_set')

    @staticmethod
    def get_members_count(instance):
        return instance.members.count()

    class Meta:
        model = Team
        fields = ('id', 'title', 'members_count', 'members', 'metrics')
