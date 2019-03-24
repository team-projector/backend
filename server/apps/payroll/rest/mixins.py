from apps.payroll.utils.metrics.user import UserMetricsCalculator


class UserMetricsMixin:
    def get_metrics(self, instance):
        from .serializers import UserMetricsSerializer

        show_metrics = self.context['request'].query_params.get('metrics', 'false') != 'false'
        if not show_metrics:
            return None

        calculator = UserMetricsCalculator()
        metrics = calculator.calculate(instance)

        return UserMetricsSerializer(metrics).data
