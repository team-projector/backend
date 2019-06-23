from rest_framework import serializers

from apps.payroll.models import SpentTime


class TimeExpenseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: SpentTime):
        data = super().to_representation(instance)

        self._adjust_base(data, instance)

        return data

    def _adjust_base(self, data, instance: SpentTime):
        from apps.development.models import Issue
        from apps.development.rest.serializers import IssueCardSerializer

        if not instance.base:
            return

        if instance.content_type.model_class() == Issue:
            data['issue'] = IssueCardSerializer(instance.base, context=self.context).data

    class Meta:
        model = SpentTime
        fields = ('id', 'created_at', 'updated_at', 'date', 'time_spent')
