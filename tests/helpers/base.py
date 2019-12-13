import datetime

from django.contrib.admin import site
from django.db import transaction
from django.forms.models import model_to_dict
from rest_framework.test import APIRequestFactory

from apps.users.services.token import create_user_token


class MockStorageMessages:
    def add(self, level, message, extra_tags):
        """Mocked add."""


class Client:
    def __init__(self, user=None):
        self.user = user
        self._factory = APIRequestFactory()
        self._credentials = {}

    def get(self, url, data=None, **extra):
        request = self._factory.get(url, data, **extra)
        request.user = self.user
        request.META.update(**self._credentials)

        return request

    def post(self, url, data, **extra):
        request = self._factory.post(url, data, **extra)
        request.user = self.user
        request.META.update(**self._credentials)

        if self.user and self.user.is_superuser:
            request._messages = MockStorageMessages()

        return request

    def put(self, url, data, **extra):
        request = self._factory.put(url, data, **extra)
        request.user = self.user
        request.META.update(**self._credentials)

        return request

    def patch(self, url, data, **extra):
        request = self._factory.patch(url, data, **extra)
        request.user = self.user
        request.META.update(**self._credentials)

        return request

    def delete(self, url, data, **extra):
        request = self._factory.delete(url, data, **extra)
        request.user = self.user
        request.META.update(**self._credentials)

        return request

    def set_credentials(self, user=None, token=None):
        if not user:
            user = self.user

        if token is None:
            token = create_user_token(user)

        self._credentials = {'HTTP_AUTHORIZATION': f'Bearer {token.key}'}


def trigger_on_commit():
    connection = transaction.get_connection()

    current_run_on_commit = connection.run_on_commit
    connection.run_on_commit = []
    while current_run_on_commit:
        sids, func = current_run_on_commit.pop(0)
        func()


def model_admin(model):
    return site._registry[model]


def model_to_dict_form(data: dict) -> dict:
    def replace(value):
        return '' if value is None else value

    original = model_to_dict(data)
    return {k: replace(v) for k, v in original.items()}


def format_date(d: datetime) -> str:
    return d.strftime('%Y-%m-%d')


def parse_gl_date(s: str) -> datetime:
    return datetime.datetime.strptime(s, '%Y-%m-%d')
