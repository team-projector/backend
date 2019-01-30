from rest_framework import status

from apps.core.tests.base import BaseAPITest


class UsersTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user_1 = self.create_user('user_1')
        self.user_2 = self.create_user('user_2')
        self.user_3 = self.create_user('user_3')
        self.user_4 = self.create_user('user_4')

    def test_links(self):
        self.set_credentials()
        response = self.client.get('/api/users/links')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_has_no_active(self):
        self.user_1.is_active = False
        self.user_1.save()

        self.user_2.is_active = False
        self.user_2.save()

        self.set_credentials()
        response = self.client.get('/api/users/links')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
