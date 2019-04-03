from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.tests.factories import MilestoneFactory


class ApiMilestonesTests(BaseAPITest):
    def test_list(self):
        MilestoneFactory.create_batch(5)

        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
