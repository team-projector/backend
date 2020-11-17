from apps.development.services.issue.related import get_related_issues
from apps.development.services.issue.tickets.updater import set_issue_ticket


def propagate_ticket_to_related_issues(issue) -> None:
    """Propagate ticket from parent issue to child."""
    if not issue.ticket:
        return

    related_issues = (
        get_related_issues(issue)
        .exclude(pk=issue.pk)
        .filter(ticket_id__isnull=True)
    )
    for related_issue in related_issues:
        set_issue_ticket(related_issue, issue.ticket)
        related_issue.save()
