from apps.development.services.milestone.metrics import MilestoneMetrics
from tests.helpers.checkers import assert_instance_fields


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
    assert_instance_fields(
        metrics,
        budget=budget,
        payroll=payroll,
        profit=profit,
        budget_remains=budget_remains,
        budget_spent=budget_spent,
        issues_count=issues_count,
        issues_opened_count=issues_opened_count,
        issues_closed_count=issues_closed_count,
    )
