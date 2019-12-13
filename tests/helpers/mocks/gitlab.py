import json
import re

import httpretty
from django.conf import settings
from rest_framework import status

RE_GITLAB_URL = re.compile(r'https://gitlab\.com.*')
BASE_GL_API_URL = f'{settings.GITLAB_HOST}/api/v4'


class GitlabMock:
    def __init__(self):
        assert httpretty.is_enabled()

        self._registry_url(httpretty.GET, RE_GITLAB_URL)
        self._registry_url(httpretty.POST, RE_GITLAB_URL)
        self._registry_url(httpretty.DELETE, RE_GITLAB_URL)

    def registry_get(self, path, data=None, status_code=status.HTTP_200_OK):
        self._registry_url(
            method=httpretty.GET,
            uri=self._prepare_uri(path),
            data=data,
            status_code=status_code,
            priority=1
        )

    def registry_post(self, path, data=None, status_code=status.HTTP_200_OK):
        self._registry_url(
            method=httpretty.POST,
            uri=self._prepare_uri(path),
            data=data,
            status_code=status_code,
            priority=1
        )

    def registry_delete(self, path, status_code=status.HTTP_200_OK):
        self._registry_url(
            method=httpretty.DELETE,
            uri=self._prepare_uri(path),
            status_code=status_code,
            priority=1
        )

    def _registry_url(
        self,
        method,
        uri,
        data=None,
        status_code=status.HTTP_200_OK,
        priority=0,
    ):
        def request_callback(request, uri, response_headers):
            response_headers['Content-Type'] = 'application/json'

            return [
                status_code,
                response_headers,
                json.dumps(data)
            ]

        httpretty.register_uri(
            method=method,
            uri=uri,
            body=request_callback,
            priority=priority
        )

    def _prepare_uri(self, path):
        return f'{BASE_GL_API_URL}{path}'