from constance import config

from apps.core.notifications import slack
from apps.development.models import Project, Ticket
from apps.development.models.label import LABEL_DONE
from apps.development.services.project.members import get_project_managers


class TicketCompletionService:
    """Service to handle tickets with the "completed" state.

    Completed state means that all issues related to the ticket have
    the label "done".
    """

    def notify_if_completed(self, ticket: Ticket):
        """Check if ticket has no uncompleted issues and send notification."""
        if self._is_ticket_completed(ticket):
            self._notify_managers(ticket)

    def _is_ticket_completed(self, ticket: Ticket):
        """Checking that Ticket doesn't have any uncompleted issues."""
        return not ticket.issues.exclude(
            labels__title__iexact=LABEL_DONE,
        ).exists()

    def _notify_managers(self, ticket: Ticket):
        """Notify project managers."""
        projects = Project.objects.filter(
            issues__in=ticket.issues.all(),
        ).distinct()

        for project in projects:
            self._send_slack_message(ticket, project)

    def _send_slack_message(self, ticket: Ticket, project: Project):
        blocks = slack.render_template_to_blocks(
            "slack/ticket_ready_for_review.json",
            {
                "gitlab_address": config.GITLAB_ADDRESS,
                "project": project,
                "ticket": ticket,
                "ticket_url": ticket.site_url,
            },
        )

        managers = get_project_managers(project)
        for manager in managers:
            slack.send_blocks(manager, blocks)


ticket_completion_service = TicketCompletionService()
