from django.test import override_settings
from rest_framework import status

from apps.development.models import Issue
from tests.base import BaseAPITest
from tests.mocks import activate_httpretty, GitlabMock
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlIssueTimeStats, GlUserFactory, GlProjectFactory,
    GlProjectsIssueFactory
)
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
        gl_mocker = GitlabMock()

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

        gl_mocker.registry_get('/user', GlUserFactory())
        gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)
        gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)
        gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/time_stats', GlIssueTimeStats())
        gl_mocker.registry_get(f'/users/{gl_assignee.id}', gl_assignee)
        gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', [])
        gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
        gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [])
        gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants', [])

        t = list(Issue.objects.allowed_for_user(self.user))

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id}/sync')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(issue.id, response.data['id'])
        self.assertEqual(issue.gl_id, response.data['gl_id'])

        issue.refresh_from_db()
        self.assertEqual(issue.state, 'closed')
