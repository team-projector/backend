from rest_framework import status

from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory


class GitlabIssueStatusTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.issue = IssueFactory.create(title='Issue 1',
                                         gl_url='https://gitlab.com/test/issues/2')

    def test_gl_url_not_valid(self):
        self.set_credentials()
        response = self.client.get('/api/gitlab/issue/status')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        params = {
            'url': 'https://test.com/test/issues/2'
        }
        response = self.client.get('/api/gitlab/issue/status', params)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_gl_url_not_found(self):
        self.set_credentials()
        params = {
            'url': 'https://gitlab.com/test/issues/0'
        }
        response = self.client.get('/api/gitlab/issue/status', params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)

    def test_retrieve(self):
        self.set_credentials()

        params = {
            'url': 'https://gitlab.com/test/issues/2'
        }
        response = self.client.get('/api/gitlab/issue/status', params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.issue.id)
        self.assertEqual(response.data[0]['title'], 'Issue 1')
        self.assertEqual(response.data[0]['state'], self.issue.state)
        self.assertEqual(response.data[0]['is_merged'], self.issue.is_merged)
