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
