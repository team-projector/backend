from apps.development.services.ticket.metrics import TicketMetrics
from tests.helpers.checkers import assert_instance_fields


def check_ticket_metrics(  # noqa: WPS211
    metrics: TicketMetrics,
    issues_count: int = 0,
    budget_estimate: float = 0.0,
    budget_spent: float = 0.0,
    budget_remains: float = 0.0,
    payroll: float = 0.0,
    profit: float = 0.0,
):
    """Check ticket metrics."""
    assert_instance_fields(
        metrics,
        issues_count=issues_count,
        budget_estimate=budget_estimate,
        budget_spent=budget_spent,
        budget_remains=budget_remains,
        payroll=payroll,
        profit=profit,
    )
