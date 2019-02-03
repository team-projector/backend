from rest_framework import serializers

from apps.development.rest.serializers import IssueCardSerializer
from apps.payroll.models import SpentTime
from apps.users.models import User


class MetricsParamsSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    start = serializers.DateField()
    end = serializers.DateField()
    group = serializers.CharField()


class MetricSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    time_spent = serializers.IntegerField()
    time_estimate = serializers.IntegerField()
    efficiency = serializers.FloatField()
    earnings = serializers.IntegerField()


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
        fields = ('id', 'created_at', 'date', 'time_spent', 'earnings')
