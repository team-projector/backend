from django.utils import timezone

from apps.development.models import Ticket
from apps.development.services.ticket.problems import (
    annotate_ticket_problems,
    checkers,
)
from tests.test_development.factories import IssueFactory, TicketFactory

_over_due_date_checker = checkers.OverDueDateChecker()


def test_has_problem(db):
    issue = IssueFactory(
        ticket=TicketFactory(due_date=timezone.now()),
        due_date=timezone.now() + timezone.timedelta(days=1),
    )
    assert _over_due_date_checker.ticket_has_problem(issue.ticket)


def test_ticket_no_due_date(db):
    issue = IssueFactory(
        ticket=TicketFactory(due_date=None),
        due_date=timezone.now() + timezone.timedelta(days=1),
    )
    assert not _over_due_date_checker.ticket_has_problem(issue.ticket)


def test_prefetched(db, django_db_blocker):
    issue = IssueFactory(
        ticket=TicketFactory(due_date=timezone.now()),
        due_date=timezone.now() + timezone.timedelta(days=1),
    )

    ticket = annotate_ticket_problems(
        Ticket.objects.filter(id=issue.ticket_id),
    ).get()

    with django_db_blocker.block():
        assert _over_due_date_checker.ticket_has_problem(ticket)
