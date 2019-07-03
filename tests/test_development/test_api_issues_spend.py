from django.test import override_settings
from rest_framework import status

from tests.base import BaseAPITest
from tests.mocks import activate_httpretty, GitlabMock
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlIssueAddSpentTimeFactory, GlProjectFactory, GlIssueFactory, GlUserFactory)

ONE_MINUTE = 60


class ApiIssuesSpendTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user.gl_token = 'token'
        self.user.save()

    def test_not_allowed(self):
        project = ProjectFactory.create()
        issue = IssueFactory.create(user=self.user, project=project)

        self.set_credentials()
        response = self.client.get(f'/api/issues/{issue.id}/spend', {'time': ONE_MINUTE})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_not_found(self):
        project = ProjectFactory.create()
        issue = IssueFactory.create(user=self.user, project=project)

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id + 1}/spend', {'time': ONE_MINUTE})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_without_body(self):
        project = ProjectFactory.create()
        issue = IssueFactory.create(user=self.user, project=project)

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id}/spend')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['time'][0], 'This field is required.')

    def test_bad_time(self):
        project = ProjectFactory.create()
        issue = IssueFactory.create(user=self.user, project=project)

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id}/spend', {'time': -ONE_MINUTE})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(f'/api/issues/{issue.id}/spend', {'time': 'test'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
    @activate_httpretty
    def test_spend(self):
        gl_mocker = GitlabMock()

        gl_project = AttrDict(GlProjectFactory())
        project = ProjectFactory.create(gl_id=gl_project.id)

        gl_project_issue = AttrDict(GlIssueFactory(id=gl_project.id))
        issue = IssueFactory.create(gl_iid=gl_project_issue.iid, user=self.user, project=project)
        IssueFactory.create_batch(5, project=project)

        gl_mocker.registry_get('/user', GlUserFactory())
        gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)
        gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_project_issue.iid}', gl_project_issue)
        gl_mocker.registry_post(f'/projects/{gl_project.id}/issues/{gl_project_issue.iid}/add_spent_time',
                              GlIssueAddSpentTimeFactory())

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id}/spend', {'time': ONE_MINUTE})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], issue.id)
        self.assertEqual(response.data['title'], issue.title)
