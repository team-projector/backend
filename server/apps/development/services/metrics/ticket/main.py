from apps.development.models import Ticket
from .provider import TicketMetrics, TicketMetricsProvider


def get_ticket_metrics(ticket: Ticket) -> TicketMetrics:
    return TicketMetricsProvider(ticket).get_metrics()
