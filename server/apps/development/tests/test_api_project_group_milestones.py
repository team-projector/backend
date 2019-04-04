from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.development.tests.factories import ProjectGroupFactory, ProjectGroupMilestoneFactory


class ApiMilestonesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.project_group = ProjectGroupFactory.create()

    def test_empty_list(self):
        self.set_credentials()
        response = self.client.get(f'/api/project-groups/{self.project_group.id}/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list(self):
        project_group_milestone = ProjectGroupMilestoneFactory.create(owner=self.project_group)
        ProjectGroupMilestoneFactory.create_batch(5)

        self.set_credentials()
        response = self.client.get(f'/api/project-groups/{self.project_group.id}/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], project_group_milestone.id)
