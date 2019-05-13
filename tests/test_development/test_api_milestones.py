from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
from tests.test_development.factories import TeamFactory, TeamMemberFactory, ProjectGroupMilestoneFactory


class ApiMilestonesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        team = TeamFactory.create()
        TeamMemberFactory.create(team=team, user=self.user, roles=TeamMember.roles.project_manager)

    def test_empty_list(self):
        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list(self):
        milestone = ProjectGroupMilestoneFactory.create()

        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], milestone.id)
