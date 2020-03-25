# -*- coding: utf-8 -*-

import datetime

from django.db import transaction
from django.forms.models import model_to_dict
from rest_framework.test import APIRequestFactory

from apps.users.services.token.create import create_user_token


class MockStorageMessages:
    def add(self, level, message, extra_tags):
        """Mocked add."""


class Client:
    def __init__(self, user=None):
        """Initializing."""
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
            request._messages = MockStorageMessages()  # noqa: WPS437

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

        self._credentials = {
            "HTTP_AUTHORIZATION": "Bearer {0}".format(token.key),
        }


def trigger_on_commit():
    connection = transaction.get_connection()

    current_run_on_commit = connection.run_on_commit
    connection.run_on_commit = []
    while current_run_on_commit:
        sids, func = current_run_on_commit.pop(0)
        func()


def model_to_dict_form(data: dict) -> dict:
    def replace(value):
        return "" if value is None else value

    original = model_to_dict(data)
    return {key: replace(value) for key, value in original.items()}


def format_date(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")
