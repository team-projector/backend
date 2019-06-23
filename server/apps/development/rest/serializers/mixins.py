from django.db.models import Sum
from rest_framework import serializers

from apps.core.utils.objects import dict2obj
from apps.payroll.models import SpentTime
from .issue_metrics import IssueMetricsSerializer
from ...models import Issue


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
