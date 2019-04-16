from rest_framework import status

from apps.users.models import Token
from tests.base import BaseAPITest, USER_PASSWORD


class LoginTests(BaseAPITest):
    def test_login(self):
        response = self.client.post('/api/login', {
            'login': self.user.login,
            'password': USER_PASSWORD
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Token.objects.filter(user=self.user, key=response.data['token']).exists())

    def test_password_not_valid(self):
        response = self.client.post('/api/login', {
            'login': self.user.login,
            'password': f'{USER_PASSWORD}bla'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_not_valid(self):
        response = self.client.post('/api/login', {
            'login': f'{self.user.login}bla',
            'password': USER_PASSWORD
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_without_login(self):
        response = self.client.post('/api/login', {
            'password': USER_PASSWORD
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_password(self):
        response = self.client.post('/api/login', {
            'login': self.user.login
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_not_active(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post('/api/login', {
            'login': self.user.login,
            'password': USER_PASSWORD
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_multitokens(self):
        response = self.client.post('/api/login', {
            'login': self.user.login,
            'password': USER_PASSWORD
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.filter(user=self.user).count(), 1)

        response = self.client.post('/api/login', {
            'login': self.user.login,
            'password': USER_PASSWORD
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.filter(user=self.user).count(), 2)
