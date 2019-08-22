import datetime

from django.db import transaction
from django.contrib.admin import site
from django.forms.models import model_to_dict
from rest_framework.test import APIRequestFactory

from apps.users.models import User
from apps.users.services.token import create_user_token

USER_LOGIN = 'test_test'
USER_PASSWORD = '1234560'


class MockStorageMessages:
    def add(self, level, message, extra_tags):
        return


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


def create_user(login=USER_LOGIN, **kwargs):
    user = User.objects.filter(login=login).first()

    if not user:
        if 'password' not in kwargs:
            kwargs['password'] = USER_PASSWORD

        user = User.objects.create_user(
            login=login,
            is_staff=False,
            **kwargs
        )
    elif 'password' in kwargs:
        user.set_password(kwargs.get('password'))
        user.save()

    return user


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
