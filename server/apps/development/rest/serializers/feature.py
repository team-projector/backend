from rest_framework import serializers

from apps.core.rest.serializers import LinkSerializer
from apps.development.services.metrics.feature import get_feature_metrics
from .issue import IssueCardSerializer
from .issues_container_metrics import IssuesContainerMetrics
from ...models import Feature, Milestone


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
