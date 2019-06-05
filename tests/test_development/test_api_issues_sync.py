from rest_framework import status

from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory


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
