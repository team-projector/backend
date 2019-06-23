from rest_framework import serializers

from apps.development.models import Milestone, Project, ProjectGroup
from apps.development.services.metrics.milestones import get_milestone_metrics
from .milestone_metrics import MilestoneMetricsSerializer
from .project import ProjectCardSerializer
from .project_group import ProjectGroupCardSerializer


class MilestoneCardSerializer(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_metrics(self, instance):
        if self.context['request'].query_params.get('metrics',
                                                    'false') == 'false':
            return None

        return MilestoneMetricsSerializer(get_milestone_metrics(instance)).data

    def get_owner(self, instance):
        serializer_class = self._get_serializer_class(
            instance.content_type.model_class())

        if not serializer_class:
            return

        data = serializer_class(instance.owner, context=self.context).data
        data['__type__'] = serializer_class.Meta.model.__name__

        return data

    @staticmethod
    def _get_serializer_class(model_class):
        if model_class == Project:
            return ProjectCardSerializer
        elif model_class == ProjectGroup:
            return ProjectGroupCardSerializer

    class Meta:
        model = Milestone
        fields = (
            'id', 'gl_id', 'gl_last_sync', 'gl_url', 'title', 'start_date',
            'due_date', 'metrics', 'owner', 'budget', 'state'
        )
