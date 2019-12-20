# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.functions import Coalesce

from apps.development.models import Issue, Ticket
from apps.development.models.issue import ISSUE_STATES
from apps.development.services.issue.metrics import IssuesContainerMetrics
from apps.payroll.models.spent_time import SECS_IN_HOUR, SpentTime


class TicketMetrics(IssuesContainerMetrics):
    """Ticket metrics."""

    budget_estimate: float = 0
    budget_spent: float = 0
    budget_remains: float = 0
    payroll: float = 0.0
    profit: float = 0


class TicketMetricsProvider:
    """Ticket metrics provider."""

    def __init__(self, ticket: Ticket):
        """Initialize self."""
        self.ticket = ticket

    def get_metrics(self) -> TicketMetrics:
        """Calculate and return metrics."""
        metrics = TicketMetrics()

        self._fill_issues_metrics(metrics)
        self._fill_payroll_metrics(metrics)

        metrics.budget_remains = metrics.budget_estimate - metrics.budget_spent
        metrics.profit = metrics.budget_estimate - metrics.payroll

        return metrics

    def _fill_issues_metrics(
        self,
        metrics: TicketMetrics,
    ) -> None:
        issues = Issue.objects.filter(ticket=self.ticket)

        if not issues:
            return

        stats = issues.aggregate(
            time_estimate=Coalesce(models.Sum('time_estimate'), 0),
            time_spent=Coalesce(models.Sum('total_time_spent'), 0),
            issues_closed_count=Coalesce(
                models.Count('id', filter=models.Q(state=ISSUE_STATES.CLOSED)),
                0,
            ),
            issues_opened_count=Coalesce(
                models.Count('id', filter=models.Q(state=ISSUE_STATES.OPENED)),
                0,
            ),
            issues_count=models.Count('*'),
            budget_estimate=Coalesce(
                models.Sum(
                    models.F('time_estimate')
                    / SECS_IN_HOUR
                    * models.F('user__customer_hour_rate'),
                    output_field=models.DecimalField(),
                ), 0,
            ),
        )

        metrics.time_estimate = stats['time_estimate']
        metrics.time_remains = stats['time_estimate'] - stats['time_spent']

        if stats['time_spent']:
            metrics.efficiency = stats['time_estimate'] / stats['time_spent']

        metrics.time_spent = stats['time_spent']

        metrics.issues_closed_count = stats['issues_closed_count']
        metrics.issues_opened_count = stats['issues_opened_count']
        metrics.issues_count = stats['issues_count']

        metrics.budget_estimate = stats['budget_estimate']

    def _fill_payroll_metrics(
        self,
        metrics: TicketMetrics,
    ) -> None:
        payroll = SpentTime.objects.filter(
            issues__ticket=self.ticket,
        ).aggregate(
            total_sum=Coalesce(models.Sum('sum'), 0),
            total_customer_sum=Coalesce(models.Sum('customer_sum'), 0),
        )

        metrics.payroll = payroll['total_sum']
        metrics.budget_spent = payroll['total_customer_sum']


def get_ticket_metrics(ticket: Ticket) -> TicketMetrics:
    """Get metrics for ticket."""
    return TicketMetricsProvider(ticket).get_metrics()
