from rest_framework import status

from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory, EpicFactory, ProjectGroupMilestoneFactory


class ApiIssuesTests(BaseAPITest):
    def test_list(self):
        IssueFactory.create_batch(5, user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_update_issue_epic(self):
        issue = IssueFactory.create()
        epic = EpicFactory.create(milestone=ProjectGroupMilestoneFactory.create())

        self.assertNotEqual(issue.epic_id, epic.id)

        self.set_credentials()
        response = self.client.patch(f'/api/issues/{issue.id}', {'epic': epic.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['epic']['id'], epic.id)

    def test_update_issue_epic_not_exist(self):
        issue = IssueFactory.create()

        self.set_credentials()
        response = self.client.patch(f'/api/issues/{issue.id}', {'epic': 0})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_issue_epic(self):
        issue = IssueFactory.create(epic=EpicFactory.create(milestone=ProjectGroupMilestoneFactory.create()))
        epic = EpicFactory.create(milestone=ProjectGroupMilestoneFactory.create())

        self.assertNotEqual(issue.epic_id, epic.id)

        self.set_credentials()
        response = self.client.patch(f'/api/issues/{issue.id}', {'epic': epic.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['epic']['id'], epic.id)
