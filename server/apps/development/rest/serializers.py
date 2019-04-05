from typing import Dict, Iterable

from bitfield.rest.fields import BitField
from django.db.models import Sum
from rest_framework import serializers

from apps.core.rest.serializers import LinkSerializer
from apps.core.utils.objects import dict2obj
from apps.development.rest.milestone_metrics import MilestoneMetricsCalculator
from apps.development.utils.problems.issues import checkers
from apps.payroll.models import SpentTime
from apps.users.models import User
from apps.users.rest.serializers import UserCardSerializer
from ..models import Issue, Label, Team, TeamMember, Milestone


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('id', 'title', 'color')


class IssueMetricsSerializer(serializers.Serializer):
    remains = serializers.IntegerField()
    efficiency = serializers.FloatField()
    payroll = serializers.FloatField()
    paid = serializers.FloatField()


class IssueCardSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    project = LinkSerializer()
    time_spent = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()
    milestone = LinkSerializer(source='issue_milestone')

    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'labels', 'project', 'due_date', 'state', 'time_estimate', 'total_time_spent', 'time_spent',
            'gl_url', 'metrics', 'milestone'
        )

    def get_metrics(self, instance: Issue):
        if self.context['request'].query_params.get('metrics', 'false') == 'false':
            return None

        payroll = SpentTime.objects.filter(issues__id=instance.id).aggregate_payrolls()

        metrics = {
            'remains': instance.time_remains,
            'efficiency': instance.efficiency,
            'payroll': payroll['total_payroll'] or 0,
            'paid': payroll['total_paid'],
        }

        return IssueMetricsSerializer(dict2obj(metrics)).data

    def get_time_spent(self, instance: Issue):
        return instance.time_spents.filter(user=self.context['request'].user) \
            .aggregate(total_spent=Sum('time_spent'))['total_spent']


class TeamCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'title')


class TeamMemberCardSerializer(serializers.ModelSerializer):
    roles = BitField()
    user = UserCardSerializer()

    class Meta:
        model = TeamMember
        fields = ('id', 'user', 'roles')


class ProblemsParamsSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class IssueProblemSerializer(serializers.Serializer):
    def to_representation(self, instance) -> Dict:
        return {
            'problems': self._get_problems(instance),
            'issue': IssueCardSerializer(instance, context=self.context).data
        }

    def _get_problems(self, instance) -> Iterable[str]:
        return [
            checker.problem_code
            for checker in checkers
            if getattr(instance, checker.annotate_field)
        ]


class TeamMemberFilterSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    roles = BitField(required=False, allow_null=True, model=TeamMember)


class MilestoneMetricsSerializer(serializers.Serializer):
    time_estimate = serializers.IntegerField()
    time_spent = serializers.IntegerField()
    time_remains = serializers.IntegerField()
    issues_count = serializers.IntegerField()
    efficiency = serializers.DecimalField(max_digits=12, decimal_places=2)
    salary = serializers.DecimalField(max_digits=12, decimal_places=2)


class MilestoneCardSerializer(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()

    @staticmethod
    def get_metrics(instance):
        metrics = MilestoneMetricsCalculator(instance).calculate()
        return MilestoneMetricsSerializer(metrics).data

    class Meta:
        model = Milestone
        fields = ('id', 'title', 'start_date', 'due_date', 'metrics')
