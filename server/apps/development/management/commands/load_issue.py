# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.core.gitlab.client import gl_client
from apps.development.models import Project, ProjectGroup


class Command(BaseCommand):
    def handle(self, *args, **options):
        group = ProjectGroup.objects.get(id=5)

        gl_group = gl_client.groups.get(id=group.gl_id)

        project = Project.objects.get(id=92)

        gl_project = gl_client.projects.get(id=project.gl_id)

        t = 0
