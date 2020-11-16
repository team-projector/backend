from django.utils import timezone

from apps.development.models import Ticket
from apps.development.models.issue import IssueState
from apps.development.services.ticket.problems import (
    annotate_ticket_problems,
    checkers,
)
from tests.test_development.factories import IssueFactory, TicketFactory

_over_due_date_checker = checkers.OverDueDateChecker()


def test_has_problem(user):
    """
    Test has problem.

    :param user:
    """
    issue = IssueFactory(
        ticket=TicketFactory(due_date=timezone.now()),
        due_date=timezone.now() + timezone.timedelta(days=1),
        user=user,
    )
    assert _over_due_date_checker.ticket_has_problem(issue.ticket)


def test_issue_state_closed(db):
    """
    Test issue state closed.

    :param db:
    """
    issue = IssueFactory(
        ticket=TicketFactory(due_date=timezone.now()),
        due_date=timezone.now() + timezone.timedelta(days=1),
        state=IssueState.CLOSED,
    )
    assert not _over_due_date_checker.ticket_has_problem(issue.ticket)


def test_ticket_no_due_date(db):
    """
    Test ticket no due date.

    :param db:
    """
    issue = IssueFactory(
        ticket=TicketFactory(due_date=None),
        due_date=timezone.now() + timezone.timedelta(days=1),
    )
    assert not _over_due_date_checker.ticket_has_problem(issue.ticket)


def test_prefetched(db, django_db_blocker):
    """
    Test prefetched.

    :param db:
    :param django_db_blocker:
    """
    issue = IssueFactory(
        ticket=TicketFactory(due_date=timezone.now()),
        due_date=timezone.now() + timezone.timedelta(days=1),
    )

    ticket = annotate_ticket_problems(
        Ticket.objects.filter(id=issue.ticket_id),
    ).get()

    with django_db_blocker.block():
        assert _over_due_date_checker.ticket_has_problem(ticket)


def test_prefetched_issue_state_closed(db, django_db_blocker):
    """
    Test prefetched issue state closed.

    :param db:
    :param django_db_blocker:
    """
    issue = IssueFactory(
        ticket=TicketFactory(due_date=timezone.now()),
        due_date=timezone.now() + timezone.timedelta(days=1),
        state=IssueState.CLOSED,
    )

    ticket = annotate_ticket_problems(
        Ticket.objects.filter(id=issue.ticket_id),
    ).get()

    with django_db_blocker.block():
        assert not _over_due_date_checker.ticket_has_problem(ticket)
