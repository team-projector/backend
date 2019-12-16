# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)


class Command(BaseCommand):
    """Load merge requests from gitlab."""

    def handle(self, *args, **options):
        """Call function."""
        MergeRequestGlManager().sync_merge_requests(full_reload=True)
