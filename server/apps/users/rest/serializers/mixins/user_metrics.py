from apps.payroll.services.metrics.user import UserMetricsCalculator


class UserMetricsMixin:
    def get_metrics(self, instance):
        from ..user_metrics import UserMetricsSerializer

        query_params = self.context['request'].query_params
        show_metrics = query_params.get('metrics', 'false') != 'false'
        if not show_metrics:
            return None

        calculator = UserMetricsCalculator()
        metrics = calculator.calculate(instance)

        return UserMetricsSerializer(metrics).data
