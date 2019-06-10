from typing import Dict, Iterable

from bitfield.rest.fields import BitField
from django.db.models import Sum
from rest_framework import serializers
from typing import Optional, Type

from apps.core.rest.serializers import LinkSerializer
from apps.core.utils.objects import dict2obj
from apps.development.services.metrics.feature import get_feature_metrics
from apps.development.services.metrics.milestones import get_milestone_metrics
from apps.development.services.problems.issues import checkers
from apps.payroll.models import SpentTime
from apps.users.models import User
from apps.users.rest.serializers import ParticipantCardSerializer, UserCardSerializer
from ..models import Feature, Issue, Label, Milestone, Project, ProjectGroup, Team, TeamMember


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('id', 'title', 'color')


class IssueMetricsSerializer(serializers.Serializer):
    remains = serializers.IntegerField()
    efficiency = serializers.FloatField()
    payroll = serializers.FloatField()
    paid = serializers.FloatField()


class IssueMetricsMixin(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()

    def get_metrics(self, instance: Issue):
        if self.context['request'].query_params.get('metrics', 'false') == 'false':
            return None

        payroll = SpentTime.objects.filter(issues__id=instance.id).aggregate_payrolls()

        metrics = {
            'remains': instance.time_remains,
            'efficiency': instance.efficiency,
            'payroll': payroll['total_payroll'],
            'paid': payroll['total_paid'],
        }

        return IssueMetricsSerializer(dict2obj(metrics)).data

    def get_time_spent(self, instance: Issue):
        return instance.time_spents.filter(
            user=self.context['request'].user
        ).aggregate(
            total_spent=Sum('time_spent')
        )['total_spent']


class IssueSerializer(IssueMetricsMixin,
                      serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    project = LinkSerializer()
    time_spent = serializers.SerializerMethodField()

    milestone = LinkSerializer()
    feature = LinkSerializer()
    participants = ParticipantCardSerializer(many=True)
    user = UserCardSerializer()

    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'labels', 'project', 'due_date', 'state', 'time_estimate', 'total_time_spent', 'time_spent',
            'gl_url', 'metrics', 'milestone', 'feature', 'participants', 'gl_last_sync', 'gl_id', 'user'
        )


class IssueCardSerializer(IssueMetricsMixin,
                          serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    project = LinkSerializer()
    time_spent = serializers.SerializerMethodField()

    milestone = LinkSerializer()
    feature = LinkSerializer()
    participants = ParticipantCardSerializer(many=True)
    user = UserCardSerializer()

    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'labels', 'project', 'due_date', 'state', 'time_estimate', 'total_time_spent', 'time_spent',
            'gl_url', 'metrics', 'milestone', 'feature', 'participants', 'gl_last_sync', 'gl_id', 'user'
        )


class IssueUpdateSerializer(serializers.ModelSerializer):
    feature = serializers.PrimaryKeyRelatedField(queryset=Feature.objects.all())

    class Meta:
        model = Issue
        fields = ('feature',)


class TeamMemberCardSerializer(serializers.ModelSerializer):
    roles = BitField()
    user = UserCardSerializer()

    class Meta:
        model = TeamMember
        fields = ('id', 'user', 'roles')


class TeamCardSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    members = TeamMemberCardSerializer(many=True)

    @staticmethod
    def get_members_count(instance):
        return instance.members.count()

    class Meta:
        model = Team
        fields = ('id', 'title', 'members_count', 'members')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'title')


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


class FeatureSerializer(serializers.ModelSerializer):
    milestone = LinkSerializer()

    class Meta:
        model = Feature
        fields = ('id', 'title', 'start_date', 'due_date', 'milestone')


class FeatureCardSerializer(serializers.ModelSerializer):
    milestone = LinkSerializer()
    issues = IssueCardSerializer(many=True)
    metrics = serializers.SerializerMethodField()

    def get_metrics(self, instance):
        return IssuesContainerMetrics(get_feature_metrics(instance)).data

    class Meta:
        model = Feature
        fields = ('id', 'title', 'start_date', 'due_date', 'milestone', 'metrics', 'issues')


class FeatureUpdateSerializer(serializers.ModelSerializer):
    milestone = serializers.PrimaryKeyRelatedField(queryset=Milestone.objects)

    class Meta:
        model = Feature
        fields = ('title', 'description', 'start_date', 'due_date', 'milestone')


class GitlabStatusSerializer(serializers.Serializer):
    services = serializers.DictField(child=serializers.DateTimeField())
    last_issues = IssueCardSerializer(many=True)
    last_sync = serializers.DateTimeField()


class IssuesContainerMetrics(serializers.Serializer):
    time_estimate = serializers.IntegerField()
    time_spent = serializers.IntegerField()
    time_remains = serializers.IntegerField()
    issues_count = serializers.IntegerField()
    issues_closed_count = serializers.IntegerField()
    issues_opened_count = serializers.IntegerField()
    efficiency = serializers.FloatField()
    payroll = serializers.FloatField()
    customer_payroll = serializers.FloatField()


class MilestoneMetricsSerializer(IssuesContainerMetrics):
    profit = serializers.IntegerField()
    budget_remains = serializers.IntegerField()


class MilestoneCardSerializer(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_metrics(self, instance):
        if self.context['request'].query_params.get('metrics', 'false') == 'false':
            return None

        return MilestoneMetricsSerializer(get_milestone_metrics(instance)).data

    def get_owner(self, instance):
        serializer_class = Optional[Type[serializers.ModelSerializer]]

        if instance.content_type.model_class() == Project:
            serializer_class = ProjectCardSerializer
        elif instance.content_type.model_class() == ProjectGroup:
            serializer_class = ProjectGroupCardSerializer

        data = serializer_class(instance.owner, context=self.context).data
        data['__type__'] = serializer_class.Meta.model.__name__

        return data

    class Meta:
        model = Milestone
        fields = ('id', 'gl_id', 'gl_last_sync', 'gl_url', 'title', 'start_date', 'due_date', 'metrics', 'owner',
                  'budget', 'state')


class GitlabIssieStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ('id', 'title', 'state', 'is_merged')


class GitlabAddSpentTimeSerializer(serializers.Serializer):
    time = serializers.IntegerField(min_value=1)


class ProjectCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'gl_id', 'gl_last_sync', 'gl_url', 'title')


class ProjectGroupCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectGroup
        fields = ('id', 'gl_id', 'gl_last_sync', 'gl_url', 'title')
