from rest_framework import serializers

from apps.payroll.models import Salary


class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = (
            'id', 'charged_time', 'payed', 'bonus', 'created_at', 'period_to', 'taxes', 'penalty', 'period_from',
            'sum', 'total'
        )
