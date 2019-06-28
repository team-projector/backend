from apps.payroll.services.metrics.user import UserMetricsProvider


class UserMetricsMixin:
    def get_metrics(self, instance):
        from ..user_metrics import UserMetricsSerializer

        query_params = self.context['request'].query_params
        show_metrics = query_params.get('metrics', 'false') != 'false'
        if not show_metrics:
            return None

        provider = UserMetricsProvider()
        metrics = provider.get_metrics(instance)

        return UserMetricsSerializer(metrics).data
