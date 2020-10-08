from datetime import datetime

from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.development.services.ticket.metrics import get_ticket_metrics
from tests.test_development.factories import IssueFactory, TicketFactory
from tests.test_development.test_services.test_tickets.test_metrics import (
    checkers,
)
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory


def test_metrics(db):
    """
    Test metrics.

    :param db:
    """
    ticket = TicketFactory.create()
    user = UserFactory.create(customer_hour_rate=3, hour_rate=2)

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=IssueFactory.create(
            ticket=ticket,
            user=user,
            total_time_spent=seconds(hours=1),
            time_estimate=seconds(hours=2),
        ),
        time_spent=seconds(hours=1),
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=IssueFactory.create(
            ticket=ticket,
            user=user,
            state=IssueState.CLOSED,
            total_time_spent=seconds(hours=2),
            time_estimate=seconds(hours=2),
        ),
        time_spent=seconds(hours=2),
    )

    checkers.check_ticket_metrics(
        get_ticket_metrics(ticket),
        issues_count=2,
        budget_estimate=12,
        budget_spent=9,
        budget_remains=3,
        payroll=6,
        profit=6,
    )
