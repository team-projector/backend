from functools import partial
import json
import httpretty
import re

from rest_framework import status

BASE_GL_API_URL = 'https://gitlab.com/api/v4'


class GitlabMock:
    def __init__(self):
        assert httpretty.is_enabled() is True

        self.registry_get()
        self.registry_post()

    def registry_get(self, path=None, data=None):
        self._registry_url(httpretty.GET, path, data)

    def registry_post(self, path=None, data=None):
        self._registry_url(httpretty.POST, path, data)

    @staticmethod
    def _registry_url(method, path=None, data=None):
        uri = f'{BASE_GL_API_URL}{path}' if path else None

        def request_callback(request, uri, response_headers):
            if path:
                response_headers['Content-Type'] = 'application/json'

            return [status.HTTP_200_OK, response_headers, json.dumps(data)]

        httpretty.register_uri(
            method=method,
            uri=uri or re.compile(r'http://.*'),
            body=request_callback,
            priority=int(bool(uri))
        )


activate_httpretty = partial(httpretty.activate, allow_net_connect=False)
