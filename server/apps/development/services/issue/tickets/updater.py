from typing import Optional

from apps.development.models import Ticket
from apps.development.models.issue import Issue
from apps.development.models.note import NoteType
from apps.development.services.extractors import extract_tickets_links
from apps.development.services.issue.related import get_related_issues


class IssueTicketProvider:
    """Issue ticket provider."""

    def __init__(self, issue: Issue):
        """Initializing."""
        self._issue = issue

    def get_ticket_for_issue(self) -> Optional[Ticket]:
        """Try to get ticket for issue."""
        ticket = self._get_from_ticket_link()
        if not ticket:
            ticket = self._get_from_issues()

        return ticket

    def _get_from_ticket_link(self) -> Optional[Ticket]:
        """
        Get from ticket link.

        :rtype: Optional[Ticket]
        """
        tickets_ids = extract_tickets_links(self._issue.description)
        tickets_ids += sum(
            (
                note.data.get("tickets", [])
                for note in self._issue.notes.all()
                if note.type == NoteType.COMMENT and note.data
            ),
            [],
        )
        if not tickets_ids:
            return None

        return Ticket.objects.filter(pk__in=tickets_ids).first()

    def _get_from_issues(self) -> Optional[Ticket]:
        """
        Get from issues.

        :rtype: Optional[Ticket]
        """
        related_issue = (
            get_related_issues(self._issue)
            .exclude(pk=self._issue.pk)
            .filter(ticket_id__isnull=False)
            .first()
        )

        if related_issue:
            return related_issue.ticket

        return None


def update_issue_ticket(issue: Issue) -> None:
    """Setting issue.ticket from related issues."""
    if issue.ticket:
        return

    provider = IssueTicketProvider(issue)
    issue.ticket = provider.get_ticket_for_issue()
