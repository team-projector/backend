from apps.development.services.issue.metrics import IssueMetrics


def check_issues_metrics(
    metrics: IssueMetrics,
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
