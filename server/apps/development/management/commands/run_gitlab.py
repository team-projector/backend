import timeit

import gitlab
from django.core.management.base import BaseCommand
import time

from apps.development.models import Project
from apps.development.services.loaders import check_project_deleted_issues

GROUP_ID = 4018796
PROJECT_ID = 9419749


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.action()

    def action(self):
        gl = gitlab.Gitlab('https://www.gitlab.com', private_token='M6wM1-ZeeCPzPm4Z9PzS')
        gl.auth()

        # t = load_module_from_app('apps.users', 'models')
        # t = 9

        # for group in gl.groups.list(all=True):
        #     print(group)

        # group = gl.groups.get(GROUP_ID)
        # for project in group.projects.list():
        #     print(project)

        #
        # try:
        #     project = gl.projects.get(9419749321321)
        # except gitlab.GitlabGetError as e:
        #     t = 0
        # #
        # load_project_issues(project, True)
        # labels = project.labels.list(all=True)
        # t = 9

        # load_project_issues(Project.objects.get(gl_id=9419749))

        gl_project = gl.projects.get(9419749)
        # gl_project = gl.projects.get(3673718)
        project = Project.objects.get(gl_id=gl_project.id)

        check_project_deleted_issues(project, gl_project)
        #
        # ids = set()
        #
        # start_time = time.time()
        # for gl_issue in gl_project.issues.list(as_list=False):
        #     ids.add(gl_issue.id)

        # print(ids)
        #
        # print(f'--- {time.time() - start_time} secs ---')

        # load_issue_notes(issue, gl_issue)
        #
        # for gl_note in gl_issue.notes.list(as_list=False, system=True, sort='asc'):
        #     # Note.objects.sync_gitlab(gl_note, issue)
        #     print(f'-- {gl_note}')

        # merge_request = project.mergerequests.get(id=1)
        #
        # print(f'-- {merge_request}')
        #
        # for note in merge_request.notes.list(all=True, system=True):
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
