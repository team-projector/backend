from rest_framework import serializers

from apps.development.rest.serializers import IssueCardSerializer
from apps.payroll.models import Salary, SpentTime


class UserMetricsSerializer(serializers.Serializer):
    payroll_closed = serializers.FloatField()
    payroll_opened = serializers.FloatField()
    bonus = serializers.FloatField()
    penalty = serializers.FloatField()
    issues_opened_count = serializers.IntegerField()
    issues_closed_spent = serializers.FloatField()
    issues_opened_spent = serializers.FloatField()


class UserProgressMetricsParamsSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    group = serializers.CharField()


class UserProgressMetricsSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    time_estimate = serializers.IntegerField()
    time_spent = serializers.IntegerField()
    time_remains = serializers.IntegerField()
    issues_count = serializers.IntegerField()
    loading = serializers.IntegerField()
    efficiency = serializers.FloatField()
    payroll = serializers.FloatField()
    paid = serializers.FloatField()


class TimeExpenseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: SpentTime):
        data = super().to_representation(instance)

        self._adjust_base(data, instance)

        return data

    def _adjust_base(self, data, instance: SpentTime):
        from apps.development.models import Issue

        if not instance.base:
            return

        if instance.content_type.model_class() == Issue:
            data['issue'] = IssueCardSerializer(instance.base, context=self.context).data

    class Meta:
        model = SpentTime
        fields = ('id', 'created_at', 'updated_at', 'date', 'time_spent')


class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = ('id', 'charged_time', 'payed', 'bonus', 'created_at', 'period_to', 'taxes', 'penalty', 'period_from',
                  'sum', 'total')
