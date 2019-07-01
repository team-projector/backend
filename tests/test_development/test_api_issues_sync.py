from django.test import override_settings
from rest_framework import status

from tests.base import BaseAPITest
from tests.mocks import activate_httpretty, GitlabMock
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlIssueTimeStats, GlUserFactory, GlProjectFactory, GlProjectsIssueFactory
)
from tests.test_users.factories import UserFactory


class ApiIssuesSyncTests(BaseAPITest):
    def test_list_not_allowed(self):
        issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/issues/{issue.id}/sync')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_not_found(self):
        issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id + 1}/sync')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
    @activate_httpretty
    def test_sync_project(self):
        gl_mock = GitlabMock()

        gl_project = AttrDict(GlProjectFactory())
        project = ProjectFactory.create(gl_id=gl_project.id)

        gl_assignee = AttrDict(GlUserFactory())
        UserFactory.create(gl_id=gl_assignee.id)

        gl_issue = AttrDict(GlProjectsIssueFactory(project_id=gl_project.id, assignee=gl_assignee, state='closed'))
        issue = IssueFactory.create(user=self.user, gl_id=gl_issue.id, gl_iid=gl_issue.iid, project=project,
                                    state='opened')

        gl_mock.registry_get('/user', GlUserFactory())
        gl_mock.registry_get(f'/projects/{gl_project.id}', gl_project)
        gl_mock.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)
        gl_mock.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/time_stats', GlIssueTimeStats())
        gl_mock.registry_get(f'/users/{gl_assignee.id}', gl_assignee)
        gl_mock.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', [])
        gl_mock.registry_get(f'/projects/{gl_project.id}/labels', [])
        gl_mock.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [])
        gl_mock.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants', [])

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id}/sync')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], issue.id)
        self.assertEqual(response.data['gl_id'], issue.gl_id)

        issue.refresh_from_db()
        self.assertEqual(issue.state, 'closed')
