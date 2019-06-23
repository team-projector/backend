from rest_framework import serializers

from apps.core.rest.serializers import LinkSerializer
from apps.development.models import Feature, Issue
from apps.users.rest.serializers import UserCardSerializer
from .label import LabelSerializer
from .mixins import IssueMetricsMixin


class IssueSerializer(IssueMetricsMixin,
                      serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    project = LinkSerializer()
    time_spent = serializers.SerializerMethodField()
    milestone = LinkSerializer()
    feature = LinkSerializer()
    participants = UserCardSerializer(many=True)
    user = UserCardSerializer()

    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'labels', 'project', 'due_date', 'state',
            'time_estimate', 'total_time_spent', 'time_spent',
            'gl_url', 'metrics', 'milestone', 'feature', 'participants',
            'gl_last_sync', 'gl_id', 'user'
        )


class IssueCardSerializer(IssueMetricsMixin,
                          serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    project = LinkSerializer()
    time_spent = serializers.SerializerMethodField()

    milestone = LinkSerializer()
    feature = LinkSerializer()
    participants = UserCardSerializer(many=True)
    user = UserCardSerializer()

    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'labels', 'project', 'due_date', 'state',
            'time_estimate', 'total_time_spent', 'time_spent',
            'gl_url', 'metrics', 'milestone', 'feature', 'participants',
            'gl_last_sync', 'gl_id', 'user'
        )


class IssueUpdateSerializer(serializers.ModelSerializer):
    feature = serializers.PrimaryKeyRelatedField(queryset=Feature.objects.all())

    class Meta:
        model = Issue
        fields = ('feature',)
