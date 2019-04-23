from rest_framework import status

from apps.users.models import User
from tests.base import BaseAPITest


class MeUserTests(BaseAPITest):
    def test_retrieve(self):
        self.user.name = 'Steve Jobs'
        self.user.gl_avatar = 'https://www.gitlab.com/ava.jpg'
        self.user.save()

        self.set_credentials()
        response = self.client.get('/api/me/user')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['name'], self.user.name)
        self.assertEqual(response.data['avatar'], self.user.gl_avatar)

    def test_retrieve_with_roles(self):
        self.user.name = 'Steve Jobs'
        self.user.roles = User.roles.developer | User.roles.team_leader
        self.user.save()

        self.set_credentials()
        response = self.client.get('/api/me/user')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['name'], self.user.name)
        self.assertEqual(set(response.data['roles']), {'developer', 'team_leader'})