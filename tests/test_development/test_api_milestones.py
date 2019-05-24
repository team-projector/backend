from decimal import Decimal

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

    @property
    def data(self):
        return {
            'title': 'Milestone 1',
            'start_date': timezone.now().date(),
            'due_date': timezone.now().date() + timezone.timedelta(days=5),
            'budget': Decimal('90000000.50'),
            'state': 'active'
        }

    def test_empty_list(self):
        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list(self):
        milestone = ProjectGroupMilestoneFactory.create(**self.data)

        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], milestone.id)
        self.assertEqual(response.data['results'][0]['title'], self.data['title'])
        self.assertEqual(response.data['results'][0]['start_date'], str(self.data['start_date']))
        self.assertEqual(response.data['results'][0]['due_date'], str(self.data['due_date']))
        self.assertEqual(response.data['results'][0]['owner']['id'], milestone.owner.id)
        self.assertEqual(response.data['results'][0]['owner']['presentation'], milestone.owner.title)
        self.assertEqual(response.data['results'][0]['budget'], str(self.data['budget']))
        self.assertEqual(response.data['results'][0]['state'], self.data['state'])

    def test_list_filter_active(self):
        milestone_1 = ProjectGroupMilestoneFactory.create(state='active')
        milestone_2 = ProjectGroupMilestoneFactory.create(state='opened')
        ProjectGroupMilestoneFactory.create_batch(3)

        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

        response = self.client.get('/api/milestones', {'active': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], milestone_1.id)

        response = self.client.get('/api/milestones', {'active': 'false'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], milestone_2.id)

    def test_list_with_metrics(self):
        milestone = ProjectGroupMilestoneFactory.create()

        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertFalse(response.data['results'][0]['metrics'])

        response = self.client.get('/api/milestones', {'metrics': 'false'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertFalse(response.data['results'][0]['metrics'])

        response = self.client.get('/api/milestones', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], milestone.id)
        self.assertTrue(all(item['metrics'] is not None for item in response.data['results']))

    def test_list_ordering(self):
        milestone_1 = ProjectGroupMilestoneFactory.create(due_date=timezone.now().date())
        milestone_2 = ProjectGroupMilestoneFactory.create(due_date=timezone.now().date() + timezone.timedelta(days=1))
        milestone_3 = ProjectGroupMilestoneFactory.create(due_date=timezone.now().date() - timezone.timedelta(days=1))
        milestone_4 = ProjectGroupMilestoneFactory.create()

        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)
        self.assertEqual(response.data['results'][0]['id'], milestone_4.id)
        self.assertEqual(response.data['results'][1]['id'], milestone_2.id)
        self.assertEqual(response.data['results'][2]['id'], milestone_1.id)
        self.assertEqual(response.data['results'][3]['id'], milestone_3.id)
