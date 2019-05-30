from django.utils import timezone
from rest_framework import status

from apps.development.models import TeamMember
from apps.users.models import User
from tests.base import BaseAPITest
from tests.test_development.factories import (FeatureFactory, ProjectGroupMilestoneFactory, TeamFactory,
                                              TeamMemberFactory)


class ApiIssuesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user.roles = User.roles.project_manager
        self.user.save()

        team = TeamFactory.create()
        TeamMemberFactory.create(team=team, user=self.user, roles=TeamMember.roles.project_manager)

        self.milestone = ProjectGroupMilestoneFactory.create()

    def get_data(self):
        return {
            'title': 'Feature 1',
            'start_date': timezone.now().date(),
            'due_date': timezone.now().date() + timezone.timedelta(days=1),
            'milestone': self.milestone.id,
        }

    def test_feature_create(self):
        data = self.get_data()

        self.set_credentials()
        response = self.client.post('/api/features', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.data['start_date'], str(data['start_date']))
        self.assertEqual(response.data['due_date'], str(data['due_date']))
        self.assertEqual(response.data['milestone']['id'], data['milestone'])

    def test_feature_update(self):
        feature = FeatureFactory.create(title='Feature 0',
                                        start_date=timezone.now().date() - timezone.timedelta(days=5),
                                        due_date=timezone.now().date(),
                                        milestone=self.milestone)
        data = self.get_data()

        self.set_credentials()
        response = self.client.patch(f'/api/features/{feature.id}', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], feature.id)

        feature.refresh_from_db()

        self.assertEqual(feature.title, data['title'])
        self.assertEqual(feature.start_date, data['start_date'])
        self.assertEqual(feature.due_date, data['due_date'])
        self.assertEqual(feature.milestone.id, data['milestone'])
