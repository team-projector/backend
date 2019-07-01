from django.test import override_settings
from rest_framework import status

from apps.development.models import Issue
from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlIssueTimeStats, GlUserFactory, GlProjectFactory,
    GlProjectsIssueFactory
)
from tests.test_development.mocks import activate_httpretty, registry_get_gl_url
from tests.test_users.factories import UserFactory


class ApiIssuesSyncTests(BaseAPITest):
    def test_list_not_allowed(self):
        issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/issues/{issue.id}/sync')

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_not_found(self):
        issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id + 1}/sync')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
    @activate_httpretty
    def test_sync_project(self):
        gl_project = AttrDict(GlProjectFactory())
        project = ProjectFactory.create(gl_id=gl_project.id)

        gl_assignee = AttrDict(GlUserFactory())
        UserFactory.create(gl_id=gl_assignee.id)

        gl_issue = AttrDict(GlProjectsIssueFactory(
            project_id=gl_project.id,
            assignee=gl_assignee,
            state='closed'
        ))

        issue = IssueFactory.create(
            user=self.user,
            gl_id=gl_issue.id,
            gl_iid=gl_issue.iid,
            project=project,
            state='opened'
        )

        registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
        registry_get_gl_url(
            f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)
        registry_get_gl_url(
            f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}',
            gl_issue)
        registry_get_gl_url(
            f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}'
            f'/time_stats', GlIssueTimeStats())
        registry_get_gl_url(f'https://gitlab.com/api/v4/users/{gl_assignee.id}',
                            gl_assignee)
        registry_get_gl_url(
            f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by',
            [])
        registry_get_gl_url(
            f'https://gitlab.com/api/v4/projects/{gl_project.id}/labels', [])
        registry_get_gl_url(
            f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}/notes',
            [])
        registry_get_gl_url(
            f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}'
            f'/participants', [])

        t = list(Issue.objects.allowed_for_user(self.user))

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id}/sync')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(issue.id, response.data['id'])
        self.assertEqual(issue.gl_id, response.data['gl_id'])

        issue.refresh_from_db()
        self.assertEqual(issue.state, 'closed')
