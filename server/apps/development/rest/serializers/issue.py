from django.db.models import Sum
from rest_framework import serializers

from apps.core.rest.serializers import LinkSerializer
from apps.core.utils.objects import dict2obj
from apps.payroll.models import SpentTime
from .issue_metrics import IssueMetricsSerializer
from .label import LabelSerializer
from ...models import Issue


class MetricsMixin(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()

    def get_metrics(self, instance: Issue):
        query_params = self.context['request'].query_params
        if query_params.get('metrics', 'false') == 'false':
            return None

        payroll = SpentTime.objects.filter(
            issues__id=instance.id
        ).aggregate_payrolls()

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


class IssueCardSerializer(MetricsMixin,
                          serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    project = LinkSerializer()
    time_spent = serializers.SerializerMethodField()
    milestone = LinkSerializer()
    feature = LinkSerializer()

    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'labels', 'project', 'due_date', 'state',
            'time_estimate', 'total_time_spent', 'time_spent',
            'gl_url', 'metrics', 'milestone', 'feature',
            'gl_last_sync', 'gl_id'
        )
