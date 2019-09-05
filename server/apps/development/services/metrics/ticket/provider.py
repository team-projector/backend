from django.db.models import QuerySet

from apps.development.models import Ticket
from ..provider import IssuesContainerMetricsProvider, IssuesContainerMetrics


class TicketMetrics(IssuesContainerMetrics):
    budget_estimate: float = 0
    budget_remains: float = 0
    budget_spent: float = 0
    payroll: float = 0.0
    profit: float = 0


class TicketMetricsProvider(IssuesContainerMetricsProvider):
    def __init__(self, ticket: Ticket):
        self.ticket = ticket

    def filter_issues(self,
                      queryset: QuerySet) -> QuerySet:
        return queryset.filter(ticket=self.ticket)

    def get_metrics(self) -> TicketMetrics:
        metrics = TicketMetrics()

        self.fill_issues_metrics(metrics)

        return metrics
