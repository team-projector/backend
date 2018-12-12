from django.core.management.base import BaseCommand

from apps.core.gitlab import get_gitlab_client
from apps.development.models import Project


class Command(BaseCommand):
    def handle(self, *args, **options):
        gl = get_gitlab_client()

        for project in Project.objects.all():
            gl_project = gl.projects.get(id=project.gl_id)

            bad_webhook_url = 'https://tp.junte.it/gl-webhook'

            for hook in gl_project.hooks.list():
                if hook.url == bad_webhook_url:
                    hook.delete()
