import gitlab
from django.core.management.base import BaseCommand

from apps.development.models import Project

GROUP_ID = 4018796
PROJECT_ID = 9419749


class Command(BaseCommand):
    def handle(self, *args, **options):
        gl = gitlab.Gitlab('https://www.gitlab.com', private_token='M6wM1-ZeeCPzPm4Z9PzS')
        gl.auth()

        # t = load_module_from_app('apps.users', 'models')
        # t = 9

        # for group in gl.groups.list(all=True):
        #     print(group)

        # group = gl.groups.get(GROUP_ID)
        # for project in group.projects.list():
        #     print(project)

        # project = Project.objects.get(gl_id=94197492)
        #
        try:
            project = gl.projects.get(9419749321321)
        except gitlab.GitlabGetError as e:
            t = 0
        #
        # load_project_issues(project, True)
        # labels = project.labels.list(all=True)
        # t = 9

        # for note in issue.notes.list(all=True):
        #     print(f'-- {note}')
        #
        # for event in project.events.list(all=True):
        #     print(event)

        # for issue in gl.issues.list(updated_after=timezone.now() - timedelta(minutes=5)):
        #     print(issue)

        # print('-' * 10)
        #

        #
        # for issue in project.issues.list(updated_after=timezone.now() - timedelta(minutes=60)):
        #     print(issue)

        # project = gl.projects.get(id=9419749)
        # issue = project.issues.get(10)
        # t = 9
