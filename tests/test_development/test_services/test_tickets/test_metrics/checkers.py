# -*- coding: utf-8 -*-

from apps.development.services.ticket.metrics import TicketMetrics


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
    assert metrics.issues_count == issues_count
    assert metrics.budget_estimate == budget_estimate
    assert metrics.budget_spent == budget_spent
    assert metrics.budget_remains == budget_remains
    assert metrics.payroll == payroll
    assert metrics.profit == profit
