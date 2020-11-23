from typing import ClassVar

from django.db import models

from apps.development.models import Ticket
from apps.development.models.issue import Issue, IssueState

PROBLEM_OVER_DUE_DATE = "OVER_DUE_DATE"
UNASSIGNED_ISSUES = "UNASSIGNED_ISSUES"


class BaseProblemChecker:
    """A base class checks ticket problems."""

    annotate_field: ClassVar[str] = ""
    problem_code: ClassVar[str] = ""

    def setup_queryset(self, queryset: models.QuerySet) -> models.QuerySet:
        """Setup queryset."""
        return queryset.annotate(
            **{self.annotate_field: self.get_annotation()},
        )

    def ticket_has_problem(self, ticket: Ticket) -> bool:
        """Method should be implemented in subclass."""
        raise NotImplementedError

    def get_annotation(self) -> models.Expression:
        """Method should be implemented in subclass."""
        raise NotImplementedError


class OverDueDateChecker(BaseProblemChecker):
    """Check ticket over due date."""

    annotate_field = "problem_over_due_date"
    problem_code = PROBLEM_OVER_DUE_DATE

    def get_annotation(self) -> models.Expression:
        """Get condition."""
        over_due_date = Issue.objects.filter(
            ticket_id=models.OuterRef("id"),
            due_date__gt=models.OuterRef("due_date"),
            state=IssueState.OPENED,
        )

        return models.Exists(over_due_date)

    def ticket_has_problem(self, ticket: Ticket) -> bool:
        """Current issue has problem."""
        if not ticket.due_date:
            return False

        prefetched = getattr(ticket, self.annotate_field, None)
        if prefetched is not None:
            return prefetched

        return ticket.issues.filter(
            due_date__gt=ticket.due_date,
            state=IssueState.OPENED,
        ).exists()


class UnassignedIssuesChecker(BaseProblemChecker):
    """If ticket has issues without user."""

    annotate_field = "unassigned_issues"
    problem_code = UNASSIGNED_ISSUES

    def get_annotation(self) -> models.Expression:
        """Get condition."""
        not_ready = Issue.objects.filter(
            ticket_id=models.OuterRef("id"),
            user__isnull=True,
        )

        return models.Exists(not_ready)

    def ticket_has_problem(self, ticket: Ticket) -> bool:
        """Current ticket has problem."""
        prefetched = getattr(ticket, self.annotate_field, None)
        if prefetched is not None:
            return prefetched

        return ticket.issues.filter(user__isnull=True).exists()
