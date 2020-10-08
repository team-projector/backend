from apps.development.models import MergeRequest
from apps.payroll.models import SpentTime
from apps.payroll.services.spent_time.summary import (
    spent_time_aggregation_service,
)


class MergeRequestMetrics:
    """Merge request metrics."""

    remains: int = 0
    efficiency: float = 0
    payroll: float = 0
    paid: float = 0


def get_merge_request_metrics(
    merge_request: MergeRequest,
) -> MergeRequestMetrics:
    """Get metrics for merge request."""
    payroll = spent_time_aggregation_service.aggregate_payrolls(
        SpentTime.objects.filter(mergerequests__id=merge_request.id),
    )

    metrics = MergeRequestMetrics()
    metrics.remains = merge_request.time_remains
    metrics.efficiency = merge_request.efficiency or 0
    metrics.payroll = payroll["total_payroll"]
    metrics.paid = payroll["total_paid"]

    return metrics
