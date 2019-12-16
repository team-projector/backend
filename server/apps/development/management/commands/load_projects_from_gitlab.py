# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.development.services.project.gl.manager import ProjectGlManager
from apps.development.tasks import sync_projects_milestones_task


class Command(BaseCommand):
    """Load projects from gitlab."""

    def handle(self, *args, **options):  # noqa: WPS110
        """Call function."""
        ProjectGlManager().sync_all_projects()
        sync_projects_milestones_task()
