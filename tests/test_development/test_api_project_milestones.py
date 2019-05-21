from rest_framework import status

from tests.base import BaseAPITest
from apps.development.models import TeamMember
from tests.test_development.factories import ProjectFactory, ProjectMilestoneFactory, TeamFactory, TeamMemberFactory


class ApiMilestonesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        team = TeamFactory.create()
        TeamMemberFactory.create(team=team, user=self.user, roles=TeamMember.roles.project_manager)

        self.project = ProjectFactory.create()

    def test_empty_list(self):
        self.set_credentials()
        response = self.client.get(f'/api/projects/{self.project.id}/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list(self):
        project_milestone = ProjectMilestoneFactory.create(owner=self.project)
        ProjectMilestoneFactory.create_batch(5)

        self.set_credentials()
        response = self.client.get(f'/api/projects/{self.project.id}/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], project_milestone.id)

    def test_metrics(self):
        ProjectMilestoneFactory.create(owner=self.project)

        self.set_credentials()
        response = self.client.get(f'/api/projects/{self.project.id}/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertTrue(all(item['metrics'] is not None for item in response.data['results']))
