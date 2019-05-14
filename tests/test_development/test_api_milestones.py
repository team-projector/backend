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

    def test_list_metrics_is_none(self):
        ProjectGroupMilestoneFactory.create()

        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertFalse(response.data['results'][0]['metrics'])

        response = self.client.get('/api/milestones', {'metrics': 'false'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertFalse(response.data['results'][0]['metrics'])

    def test_list_metrics_empty(self):
        milestone = ProjectGroupMilestoneFactory.create()
        metrics = {
            'time_estimate': 0,
            'time_spent': 0,
            'time_remains': 0,
            'issues_count': 0,
            'efficiency': 0.0,
            'salary': 0.0
        }

        self.set_credentials()
        response = self.client.get('/api/milestones', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], milestone.id)
        self.assertEqual(response.data['results'][0]['metrics'], metrics)
