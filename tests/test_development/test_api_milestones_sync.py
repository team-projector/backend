from rest_framework import status

from tests.base import BaseAPITest
from tests.test_development.factories import ProjectGroupMilestoneFactory


class ApiMilestoneSyncTests(BaseAPITest):
    def test_list_not_allowed(self):
        milestone = ProjectGroupMilestoneFactory.create()

        self.set_credentials()
        response = self.client.get(f'/api/milestones/{milestone.id}/sync')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_not_found(self):
        milestone = ProjectGroupMilestoneFactory.create()

        self.set_credentials()
        response = self.client.post(f'/api/milestones/{milestone.id + 1}/sync')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
