import datetime
import os
import sys

from django.db import transaction
from rest_framework.test import APITestCase

from apps.users.models import User
from apps.users.utils.token import create_user_token

USER_LOGIN = 'test_test'
USER_PASSWORD = '1234560'


class BaseTestMixin:
    def setUp(self):
        super().setUp()

        self.user = self.create_user()

        self.opened_files = []

    def tearDown(self):
        super().tearDown()

        for f in self.opened_files:
            if not f.closed:
                f.close()

    @staticmethod
    def trigger_on_commit():
        connection = transaction.get_connection()

        current_run_on_commit = connection.run_on_commit
        connection.run_on_commit = []
        while current_run_on_commit:
            sids, func = current_run_on_commit.pop(0)
            func()

    @classmethod
    def create_user(cls, login=USER_LOGIN, **kwargs):
        user = User.objects.filter(login=login).first()

        if not user:
            if 'password' not in kwargs:
                kwargs['password'] = USER_PASSWORD

            user = User.objects.create_user(login=login, is_staff=False, **kwargs)
        elif 'password' in kwargs:
            user.set_password(kwargs.get('password'))
            user.save()

        return user

    def open_asset(self, filename, mode='rb', encoding=None):
        module_path = os.path.abspath(sys.modules[self.__module__].__file__)
        f = open(os.path.join(os.path.dirname(module_path), 'assets', filename), mode, encoding=encoding)

        self.opened_files.append(f)
        return f


class BaseAPITest(BaseTestMixin, APITestCase):
    def set_credentials(self, user=None, token=None):
        if not user:
            user = self.user

        if token is None:
            token = create_user_token(user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')

    def add_client_header(self, key, value):
        self.client._credentials[key] = value

    def clear_client_headers(self):
        self.client._credentials = {}

    @staticmethod
    def format_date(d: datetime) -> str:
        return d.strftime('%Y-%m-%d')

    @staticmethod
    def parse_gl_date(s: str) -> datetime:
        return datetime.datetime.strptime(s, '%Y-%m-%d')
