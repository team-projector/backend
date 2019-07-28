from rest_framework import status

from tests.base import BaseAPITest
from tests.test_users.factories import UserFactory


class UsersTests(BaseAPITest):
    def test_retrieve_inactive(self):
        user = UserFactory.create(is_active=False)

        self.set_credentials()
        response = self.client.get(f'/api/users/{user.id}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
