import gitlab
from django.core.management.base import BaseCommand

from apps.core.gitlab import get_gitlab_client
from apps.development.models import Project
from apps.development.services.gitlab.projects import check_project_webhooks


class Command(BaseCommand):
    def handle(self, *args, **options):
        gl = get_gitlab_client()

        for project in Project.objects.all():
            try:
                # self.clear_project_bad_webhooks(project, gl)
                self.validate_project_webhooks(project, gl)
            except Exception as e:
                pass

            print(f'Project "{project}" processed')

    def clear_project_bad_webhooks(self,
                                   project: Project,
                                   gl: gitlab.Gitlab):
        gl_project = gl.projects.get(id=project.gl_id)

        bad_webhook_urls = [
            'https://tp.junte.it/gl-webhook',
            'https://tp.junte.it/api/gl-webhook'
        ]

        for hook in gl_project.hooks.list():
            if hook.url in bad_webhook_urls:
                hook.delete()

    def validate_project_webhooks(self,
                                  project: Project,
                                  gl: gitlab.Gitlab):
        gl_project = gl.projects.get(id=project.gl_id)

        check_project_webhooks(gl_project)
