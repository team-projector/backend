from datetime import timedelta

import gitlab
from django.core.management.base import BaseCommand
from django.utils import timezone

GROUP_ID = 4018796
PROJECT_ID = 9419749


class Command(BaseCommand):
    def handle(self, *args, **options):
        gl = gitlab.Gitlab('https://www.gitlab.com', private_token='M6wM1-ZeeCPzPm4Z9PzS')
        gl.auth()

        # for group in gl.groups.list(all=True):
        #     print(group)

        # group = gl.groups.get(GROUP_ID)
        # for project in group.projects.list():
        #     print(project)

        project = gl.projects.get(PROJECT_ID)

        print(project)
        print('-' * 10)
        # for issue in project.issues.list(all=True)[:1]:
        #     print(f'issue {issue}:')
        #     for note in issue.notes.list(all=True):
        #         print(f'-- {note}')
        #
        for event in project.events.list(all=True):
            print(event)

        # for issue in gl.issues.list(updated_after=timezone.now() - timedelta(minutes=5)):
        #     print(issue)

        print('-' * 10)

        for issue in project.issues.list(updated_after=timezone.now() - timedelta(minutes=5)):
            print(issue)
