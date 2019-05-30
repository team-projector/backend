from rest_framework import status

from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory


class GitlabIssueStatusTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.issue = IssueFactory.create(title='Issue 1', gl_url='https://www.gitlab.com/test/issues/1')

    def test_gl_url_not_found(self):
        params = {
            'url': 'https://www.gitlab.com/test/issues/2'
        }
        response = self.client.get('/api/gitlab/issue/status', params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        params = {
            'url': 'https://www.gitlab.com/test/issues/1'
        }
        response = self.client.get('/api/gitlab/issue/status', params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.issue.id)
        self.assertEqual(response.data['title'], 'Issue 1')
        self.assertEqual(response.data['state'], self.issue.state)
        self.assertEqual(response.data['is_merged'], self.issue.is_merged)
