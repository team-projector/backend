from typing import Dict, Iterable

from actstream.models import Action
from bitfield.rest.fields import BitField
from django.apps import apps as django_apps
from django.db.models import Sum
from rest_framework import serializers

from apps.core.activity.verbs import ACTION_GITLAB_WEBHOOK_TRIGGERED, ACTION_GITLAB_CALL_API
from apps.core.db.mixins import GitlabEntityMixin
from apps.core.rest.serializers import LinkSerializer
from apps.core.utils.objects import dict2obj
from apps.development.rest.milestone_metrics import MilestoneMetricsCalculator
from apps.development.services.problems.issues import checkers
from apps.payroll.models import SpentTime
from apps.users.models import User
from apps.users.rest.serializers import UserCardSerializer, ParticipantCardSerializer
from ..models import Issue, Label, Team, TeamMember, Milestone, Epic


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
    milestone = LinkSerializer()
    epic = LinkSerializer()
    participants = ParticipantCardSerializer(many=True)

    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'labels', 'project', 'due_date', 'state', 'time_estimate', 'total_time_spent', 'time_spent',
            'gl_url', 'metrics', 'milestone', 'epic', 'participants'
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


class IssueUpdateSerializer(serializers.ModelSerializer):
    epic = serializers.PrimaryKeyRelatedField(queryset=Epic.objects.all())

    class Meta:
        model = Issue
        fields = ('epic',)


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
    efficiency = serializers.FloatField()
    salary = serializers.FloatField()


class MilestoneCardSerializer(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()

    @staticmethod
    def get_metrics(instance):
        metrics = MilestoneMetricsCalculator(instance).calculate()
        return MilestoneMetricsSerializer(metrics).data

    class Meta:
        model = Milestone
        fields = ('id', 'title', 'start_date', 'due_date', 'metrics')


class EpicSerializer(serializers.ModelSerializer):
    milestone = LinkSerializer()

    class Meta:
        model = Epic
        fields = ('id', 'title', 'start_date', 'due_date', 'milestone')


class EpicCardSerializer(serializers.ModelSerializer):
    milestone = LinkSerializer()

    class Meta:
        model = Epic
        fields = ('id', 'title', 'start_date', 'due_date', 'milestone')


class EpicUpdateSerializer(serializers.ModelSerializer):
    milestone = serializers.PrimaryKeyRelatedField(queryset=Milestone.objects)

    class Meta:
        model = Epic
        fields = ('title', 'description', 'start_date', 'due_date', 'milestone')


class GitlabStatusSerializer(serializers.Serializer):
    services = serializers.SerializerMethodField()
    last_issues = serializers.SerializerMethodField()
    last_sync = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_webhook = None
        self._last_api = None

    def get_services(self, *args):
        self.fill_services()
        return {
            'api': self._last_api,
            'web_hooks': self._last_webhook,
        }

    def get_last_issues(self, request):
        issues = Issue.objects.order_by('-updated_at')[:10]
        return IssueCardSerializer(issues, many=True, context=self.context).data

    @staticmethod
    def get_last_sync(*args):
        querysets = [
            x.objects.filter(gl_last_sync__isnull=False).values('gl_last_sync') for x in django_apps.get_models() if
            issubclass(x, GitlabEntityMixin)
        ]
        value = querysets[0].union(*querysets[1:]).order_by('-gl_last_sync').first() or {}
        return value.get('gl_last_sync')

    def fill_services(self):
        field_maps = {
            '_last_webhook': ACTION_GITLAB_WEBHOOK_TRIGGERED,
            '_last_api': ACTION_GITLAB_CALL_API
        }

        for key, value in field_maps.items():
            if not getattr(self, key):
                action = Action.objects.filter(verb=value).order_by('-timestamp').first()
                if action:
                    setattr(self, key, action.timestamp)


class MilestoneAllProjectProjectGroupCardSerializer(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()

    def get_metrics(self, instance):
        if self.context['request'].query_params.get('metrics', 'false') == 'false':
            return None

        metrics = MilestoneMetricsCalculator(instance).calculate()
        return MilestoneMetricsSerializer(metrics).data

    class Meta:
        model = Milestone
        fields = ('id', 'title', 'start_date', 'due_date', 'metrics')
