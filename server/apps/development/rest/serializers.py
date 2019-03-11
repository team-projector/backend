from typing import Dict, Iterable

from bitfield.rest.fields import BitField
from django.db.models import Sum
from rest_framework import serializers

from apps.core.rest.serializers import LinkSerializer
from apps.development.utils.problems.issues import checkers
from apps.users.models import User
from apps.users.rest.serializers import UserCardSerializer
from ..models import Issue, Label, Team, TeamMember


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('id', 'title', 'color')


class IssueCardSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    project = LinkSerializer()
    time_spent = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'labels', 'project', 'due_date', 'state', 'time_estimate', 'total_time_spent', 'time_spent',
            'gl_url', 'time_remains', 'efficiency'
        )

    def get_time_spent(self, instance):
        return instance.time_spents.filter(employee=self.context['request'].user) \
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
