from django.db.models import QuerySet
from rest_framework import serializers

from apps.core.utils.objects import dict2obj
from apps.development.models import Team, TeamMember, Issue
from apps.development.rest.serializers.team_metrics import TeamMetricsSerializer
from apps.development.services.problems.issues import (
    filter_issues_problems, annotate_issues_problems
)
from .team_member import TeamMemberCardSerializer


class TeamMetricsMixin(serializers.Serializer):
    metrics = serializers.SerializerMethodField()

    def get_metrics(self, instance: Team) -> dict:
        issues = self._get_issues(instance)

        metrics = {
            'issues_count': issues.count(),
            'problems_count': self._get_problems_count(issues)
        }

        return TeamMetricsSerializer(dict2obj(metrics)).data

    def _get_issues(self, team: Team) -> QuerySet:
        users = TeamMember.objects.get_no_watchers(team)
        return Issue.objects.filter(user__in=users)

    def _get_problems_count(self, issues: QuerySet) -> int:
        issues = annotate_issues_problems(issues)
        issues = filter_issues_problems(issues)

        return issues.count()


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
