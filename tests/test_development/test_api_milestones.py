from django.utils import timezone
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

    def test_list_filter_active(self):
        ProjectGroupMilestoneFactory.create()
        milestone_1 = ProjectGroupMilestoneFactory.create(start_date=timezone.now() - timezone.timedelta(days=3),
                                                          due_date=timezone.now() + timezone.timedelta(days=2))
        milestone_2 = ProjectGroupMilestoneFactory.create(start_date=timezone.now() - timezone.timedelta(days=3),
                                                          due_date=timezone.now() - timezone.timedelta(days=2))

        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

        response = self.client.get('/api/milestones', {'active': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn(milestone_1.id, [x['id'] for x in response.data['results']])

        response = self.client.get('/api/milestones', {'active': 'false'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn(milestone_2.id, [x['id'] for x in response.data['results']])

    def test_list_without_metrics(self):
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

    def test_list_with_metrics(self):
        milestone = ProjectGroupMilestoneFactory.create()

        self.set_credentials()
        response = self.client.get('/api/milestones', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], milestone.id)
        self.assertTrue(all(item['metrics'] is not None for item in response.data['results']))
