# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.core.gitlab import get_gitlab_client
from apps.development.services.gitlab.issues import load_issues


class Command(BaseCommand):
    def handle(self, *args, **options):
        gl = get_gitlab_client()

        junte_ui_project = gl.projects.get(id=9560752)
        junte_ui_issue = junte_ui_project.issues.get(462)

        tp_project = gl.projects.get(id=9383004)
        tp_issue = tp_project.issues.get(221)

        t = 0
