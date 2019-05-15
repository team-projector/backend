from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
from tests.test_development.factories import TeamFactory, TeamMemberFactory, ProjectGroupMilestoneFactory, FeatureFactory


class ApiMilestoneFeaturesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        team = TeamFactory.create()
        TeamMemberFactory.create(team=team, user=self.user, roles=TeamMember.roles.project_manager)

        self.milestone = ProjectGroupMilestoneFactory.create()

    def test_empty_list(self):
        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/features')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list(self):
        feature = FeatureFactory.create(milestone=self.milestone)

        milestone = ProjectGroupMilestoneFactory.create()
        FeatureFactory.create_batch(5, milestone=milestone)

        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/features')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], feature.id)
        self.assertEqual(response.data['results'][0]['milestone']['id'], self.milestone.id)
