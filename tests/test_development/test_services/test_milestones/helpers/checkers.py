from apps.development.services.milestone.metrics import MilestoneMetrics


def check_milestone_metrics(  # noqa: WPS211
    metrics: MilestoneMetrics,
    budget: float = 0.0,
    payroll: float = 0.0,
    profit: float = 0.0,
    budget_remains: float = 0.0,
    budget_spent: float = 0.0,
    issues_count: int = 0,
    issues_opened_count: int = 0,
    issues_closed_count: int = 0,
):
    """Check milestone metrics."""
    assert metrics.budget == budget
    assert metrics.payroll == payroll
    assert metrics.profit == profit
    assert metrics.budget_remains == budget_remains
    assert metrics.budget_spent == budget_spent
    assert metrics.issues_count == issues_count
    assert metrics.issues_opened_count == issues_opened_count
    assert metrics.issues_closed_count == issues_closed_count
