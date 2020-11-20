from typing import Set

from apps.development.models.issue import Issue
from apps.development.models.label import LABEL_DONE, Label
from apps.development.tasks import notify_if_ticket_completed_task


def on_issue_labeling(issue: Issue, labels_ids: Set[int]):
    """This service used as an entry point for the m2m signal."""
    handle_done_label(issue, labels_ids)


def handle_done_label(issue: Issue, labels_ids):
    """Here we process the logic associated with adding the "done" label."""
    if not issue.ticket:
        return

    done_label = Label.objects.filter(title__iexact=LABEL_DONE).first()
    if not done_label:
        return

    if done_label.pk not in labels_ids:
        return

    notify_if_ticket_completed_task.delay(issue.ticket.pk)
