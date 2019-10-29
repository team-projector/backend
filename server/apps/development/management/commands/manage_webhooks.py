# -*- coding: utf-8 -*-

import gitlab
from django.core.management.base import BaseCommand

from apps.core.gitlab.client import gl_client
from apps.development.models import Project
from apps.development.services.project.gitlab import check_project_webhooks


class Command(BaseCommand):
    def handle(self, *args, **options):

        for project in Project.objects.all():
            try:
                # self.clear_project_bad_webhooks(project, gl)
                self.validate_project_webhooks(project)
            except Exception as e:
                pass

            print(f'Project "{project}" processed')

    def clear_project_bad_webhooks(
        self,
        project: Project,
        gl: gitlab.Gitlab,
    ):
        gl_project = gl.projects.get(id=project.gl_id)

        bad_webhook_urls = [
            'https://tp.junte.it/gl-webhook',
            'https://tp.junte.it/api/gl-webhook'
        ]

        for hook in gl_project.hooks.list():
            if hook.url in bad_webhook_urls:
                hook.delete()

    def validate_project_webhooks(
        self,
        project: Project
    ):
        gl_project = gl_client.projects.get(id=project.gl_id)

        check_project_webhooks(gl_project)
