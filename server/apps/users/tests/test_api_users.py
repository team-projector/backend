from rest_framework import status

from apps.core.tests.base import BaseAPITest
from apps.users.tests.factories import UserFactory


class UsersTests(BaseAPITest):
    def test_links(self):
        UserFactory.create_batch(5)

        self.set_credentials()

        response = self.client.get('/api/users/links')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)

    def test_has_no_active(self):
        UserFactory.create_batch(3)
        UserFactory.create_batch(2, is_active=False)

        self.set_credentials()
        response = self.client.get('/api/users/links')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_retrieve(self):
        user = UserFactory.create()

        self.set_credentials()
        response = self.client.get(f'/api/users/{user.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['login'], user.login)

    def test_retrieve_inactive(self):
        user = UserFactory.create(is_active=False)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user.id}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_not_exists(self):
        self.set_credentials()
        response = self.client.get(f'/api/users/{self.user.id + 1}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
