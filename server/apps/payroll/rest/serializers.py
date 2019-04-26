from rest_framework import serializers

from apps.core.rest.serializers import LinkSerializer
from apps.development.rest.serializers import IssueCardSerializer
from apps.payroll.models import Salary, SpentTime, WorkBreak
from apps.users.rest.serializers import UserCardSerializer


class UserMetricsSerializer(serializers.Serializer):
    payroll_closed = serializers.FloatField()
    payroll_opened = serializers.FloatField()
    bonus = serializers.FloatField()
    penalty = serializers.FloatField()
    issues_opened_count = serializers.IntegerField()


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


class WorkBreakSerializer(serializers.ModelSerializer):
    approved_by = UserCardSerializer()
    user = LinkSerializer()
    approved_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    from_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    to_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = WorkBreak
        fields = ('approve_state', 'approved_by', 'approved_at', 'decline_reason', 'comment', 'from_date', 'reason',
                  'to_date', 'id', 'user')


class WorkBreakCardSerializer(WorkBreakSerializer):
    approved_by = LinkSerializer()


class WorkBreakUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkBreak
        fields = ('approve_state', 'approved_by', 'approved_at', 'decline_reason', 'comment', 'from_date', 'reason',
                  'to_date', 'id', 'user')
