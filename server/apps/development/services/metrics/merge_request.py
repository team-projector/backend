from apps.payroll.models import SpentTime


class MergeRequestMetrics:
    remains: int = 0
    efficiency: float = 0
    payroll: float = 0
    paid: float = 0


def get_merge_request_metrcis(merge_request) -> MergeRequestMetrics:
    payroll = SpentTime.objects.filter(
        mergerequests__id=merge_request.id,
    ).aggregate_payrolls()

    metrics = MergeRequestMetrics()
    metrics.remains = merge_request.time_remains
    metrics.efficiency = merge_request.efficiency
    metrics.payroll = payroll['total_payroll']
    metrics.paid = payroll['total_paid']

    return metrics
