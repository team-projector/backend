import httpretty
from django.test import override_settings
from rest_framework import status

from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.mocks import BaseGitlabMockTests

ONE_MINUTE = 60


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
class ApiIssuesSpendTests(BaseAPITest, BaseGitlabMockTests):
    def setUp(self):
        super().setUp()

        self.user.gl_token = 'token'
        self.user.save()

    @httpretty.activate
    def test_not_allowed(self):
        project = ProjectFactory.create()
        issue = IssueFactory.create(user=self.user, project=project)

        self._registry_gl_urls(project.gl_id, issue.gl_iid)

        self.set_credentials()
        response = self.client.get(f'/api/issues/{issue.id}/spend', {'time': ONE_MINUTE})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.disable_url()

    @httpretty.activate
    def test_not_found(self):
        project = ProjectFactory.create()
        issue = IssueFactory.create(user=self.user, project=project)

        self._registry_gl_urls(project.gl_id, issue.gl_iid)

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id + 1}/spend', {'time': ONE_MINUTE})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.disable_url()

    @httpretty.activate
    def test_post_without_body(self):
        project = ProjectFactory.create()
        issue = IssueFactory.create(user=self.user, project=project)

        self._registry_gl_urls(project.gl_id, issue.gl_iid)

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id}/spend')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['time'][0], 'This field is required.')

        self.disable_url()

    @httpretty.activate
    def test_bad_time(self):
        project = ProjectFactory.create()
        issue = IssueFactory.create(user=self.user, project=project)

        self._registry_gl_urls(project.gl_id, issue.gl_iid)

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id}/spend', {'time': -ONE_MINUTE})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(f'/api/issues/{issue.id}/spend', {'time': 'test'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.disable_url()

    @httpretty.activate
    def test_spend(self):
        project = ProjectFactory.create()
        issue = IssueFactory.create(user=self.user, project=project)
        IssueFactory.create_batch(5, project=project)

        self._registry_gl_urls(project.gl_id, issue.gl_iid)

        self.set_credentials()
        response = self.client.post(f'/api/issues/{issue.id}/spend', {'time': ONE_MINUTE})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], issue.id)
        self.assertEqual(response.data['title'], issue.title)

        self.disable_url()

    def _registry_gl_urls(self, project_id: int, issue_id: int) -> None:
        self.registry_user()
        self.registry_project(project_id)
        self.registry_project_issue(project_id, issue_id)
        self.registry_issue_add_spent_time(project_id, issue_id)
