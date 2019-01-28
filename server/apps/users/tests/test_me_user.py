from rest_framework import status

from apps.core.tests.base import BaseAPITest


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
        self.assertEqual(response.data['gl_avatar'], self.user.gl_avatar)
