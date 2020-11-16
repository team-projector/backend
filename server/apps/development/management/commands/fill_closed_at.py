from datetime import timedelta

from django.core.management.base import BaseCommand

from apps.development.models import Issue
from apps.development.models.issue import IssueState


class Command(BaseCommand):
    """Fill close at for old issues."""

    def handle(self, *args, **options):  # noqa: WPS110
        """Call function."""
        issues = Issue.objects.filter(
            closed_at__isnull=True,
            state=IssueState.CLOSED,
        )

        for issue in issues:
            issue.closed_at = issue.created_at + timedelta(hours=1)
            issue.save()
