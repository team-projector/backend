from apps.development.services.merge_request.metrics import MergeRequestMetrics


def check_merge_request_metrics(
    metrics: MergeRequestMetrics,
    remains: int = 0,
    efficiency: float = 0,
    payroll: float = 0,
    paid: float = 0,
):
    """Check issue metrics."""
    assert metrics.remains == remains
    assert metrics.efficiency == efficiency
    assert metrics.payroll == payroll
    assert metrics.paid == paid
