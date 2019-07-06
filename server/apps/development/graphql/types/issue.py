import graphene
from graphene_django import DjangoObjectType

from apps.development.models import Issue
from apps.payroll.models import SpentTime
from .issue_metrics import IssueMetrics


class IssueType(DjangoObjectType):
    class Meta:
        model = Issue

    metrics = graphene.Field(IssueMetrics)

    def resolve_metrics(self, info, **kwargs):
        instance: Issue = self

        payroll = SpentTime.objects.filter(
            issues__id=instance.id
        ).aggregate_payrolls()

        return {
            'remains': instance.time_remains,
            'efficiency': instance.efficiency,
            'payroll': payroll['total_payroll'],
            'paid': payroll['total_paid'],
        }
