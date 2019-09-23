from datetime import datetime

from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES
from apps.development.services.metrics.ticket import get_ticket_metrics
from tests.test_development.factories import IssueFactory, TicketFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


def test_metrics(db):
    ticket = TicketFactory.create()
    user = UserFactory.create(customer_hour_rate=3,
                              hour_rate=2)

    issue_1 = IssueFactory.create(
        ticket=ticket,
        user=user,
        state=ISSUE_STATES.opened,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_1,
        time_spent=seconds(hours=1)
    )

    issue_2 = IssueFactory.create(
        ticket=ticket,
        user=user,
        state=ISSUE_STATES.closed,
        total_time_spent=seconds(hours=2),
        time_estimate=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_2,
        time_spent=seconds(hours=2)
    )

    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_count == 2

    assert metrics.budget_estimate == 12
    assert metrics.budget_spent == 9
    assert metrics.budget_remains == 3

    assert metrics.payroll == 6
    assert metrics.profit == 6
