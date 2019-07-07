from datetime import datetime
from decimal import Decimal

from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from apps.users.models import User
from apps.development.models import Milestone, Project, ProjectGroup
from tests.base import BaseAPITest
from tests.test_development.factories import ProjectMilestoneFactory, ProjectGroupMilestoneFactory


class ApiMilestonesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user.roles = User.roles.project_manager
        self.user.save()

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
        self.assertEqual(response.data['results'][0]['gl_id'], milestone.gl_id)
        self.assertEqual(response.data['results'][0]['gl_last_sync'], milestone.gl_last_sync)
        self.assertEqual(response.data['results'][0]['gl_url'], milestone.gl_url)
        self.assertEqual(response.data['results'][0]['title'], self.data['title'])
        self.assertEqual(response.data['results'][0]['start_date'], str(self.data['start_date']))
        self.assertEqual(response.data['results'][0]['due_date'], str(self.data['due_date']))
        self.assertEqual(response.data['results'][0]['budget'], self.data['budget'])
        self.assertEqual(response.data['results'][0]['state'], self.data['state'])

    def test_list_filter_active(self):
        milestone_1 = ProjectGroupMilestoneFactory.create(state='active')
        milestone_2 = ProjectGroupMilestoneFactory.create(state='closed')
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
        milestone_1 = ProjectGroupMilestoneFactory.create(due_date=datetime.now().date())
        milestone_2 = ProjectGroupMilestoneFactory.create(due_date=datetime.now().date() + timezone.timedelta(days=1))
        milestone_3 = ProjectGroupMilestoneFactory.create(due_date=datetime.now().date() - timezone.timedelta(days=1))
        milestone_4 = ProjectGroupMilestoneFactory.create()

        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)
        self.assertEqual(response.data['results'][0]['id'], milestone_4.id)
        self.assertEqual(response.data['results'][1]['id'], milestone_2.id)
        self.assertEqual(response.data['results'][2]['id'], milestone_1.id)
        self.assertEqual(response.data['results'][3]['id'], milestone_3.id)

    def test_list_owner_type(self):
        milestone_1 = ProjectMilestoneFactory.create()
        milestone_2 = ProjectGroupMilestoneFactory.create()
        milestone_3 = Milestone.objects.create(gl_id=milestone_2.gl_id + 1, gl_url=f'{milestone_2.gl_id}test',
                                               owner=self.user, object_id=self.user.id,
                                               content_type=ContentType.objects.get_for_model(User))

        self.set_credentials()
        response = self.client.get('/api/milestones')

        self.assertEqual(response.data['count'], 3)
        self._check_project_group(milestone_1, response.data['results'], owner=Project)
        self._check_project_group(milestone_2, response.data['results'], owner=ProjectGroup)
        self._check_project_group(milestone_3, response.data['results'])

    def _check_project_group(self, milestone, results, owner=None):
        self.assertIn(milestone.id, [x['id'] for x in results])

        if owner:
            self.assertIn(milestone.owner.id, [x['owner']['id'] for x in results if x['owner']])
            self.assertIn(milestone.owner.gl_id, [x['owner']['gl_id'] for x in results if x['owner']])
            self.assertIn(milestone.owner.gl_last_sync, [x['owner']['gl_last_sync'] for x in results if x['owner']])
            self.assertIn(milestone.owner.title, [x['owner']['title'] for x in results if x['owner']])
            self.assertIn(owner.__name__, [x['owner']['__type__'] for x in results if x['owner']])
        else:
            self.assertTrue([True for x in results if not x['owner']])
