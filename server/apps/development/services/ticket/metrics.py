# -*- coding: utf-8 -*-

from django.db.models import Count, DecimalField, F, Q, Sum
from django.db.models.functions import Coalesce

from apps.development.models import Issue, Ticket
from apps.development.models.issue import ISSUE_STATES
from apps.development.services.issue import IssuesContainerMetrics
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

        stats = issues.aggregate(
            time_estimate=Coalesce(Sum('time_estimate'), 0),
            time_spent=Coalesce(Sum('total_time_spent'), 0),
            issues_closed_count=Coalesce(
                Count('id', filter=Q(state=ISSUE_STATES.closed)), 0,
            ),
            issues_opened_count=Coalesce(
                Count('id', filter=Q(state=ISSUE_STATES.opened)), 0,
            ),
            issues_count=Count('*'),
            budget_estimate=Coalesce(
                Sum(
                    F('time_estimate')
                    / SECS_IN_HOUR
                    * F('user__customer_hour_rate'),
                    output_field=DecimalField(),
                ), 0,
            ),
        )

        if not stats:
            return

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
            total_sum=Coalesce(Sum('sum'), 0),
            total_customer_sum=Coalesce(Sum('customer_sum'), 0),
        )

        metrics.payroll = payroll['total_sum']
        metrics.budget_spent = payroll['total_customer_sum']


def get_ticket_metrics(ticket: Ticket) -> TicketMetrics:
    """Get metrics for ticket."""
    return TicketMetricsProvider(ticket).get_metrics()