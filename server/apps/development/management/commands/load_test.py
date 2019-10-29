# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.core.gitlab.client import get_default_gitlab_client
from apps.development.models import Project


class Command(BaseCommand):
    def handle(self, *args, **options):
        gl_client = get_default_gitlab_client()

        project = Project.objects.get(id=109)

        gl_project = gl_client.projects.get(id=project.gl_id)

        t = 0
