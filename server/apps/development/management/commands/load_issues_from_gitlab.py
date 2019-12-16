# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.development.services.issue.gl.manager import IssueGlManager


class Command(BaseCommand):
    """Load issues from gitlab."""

    def handle(self, *args, **options):
        """Call function."""
        IssueGlManager().sync_issues(full_reload=True)
