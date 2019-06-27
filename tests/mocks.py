from functools import partial
import json
import httpretty

GL_API_URL = 'https://gitlab.com/api/v4'


class GitlabMock:
    def registry_get(self, path, data):
        self._registry_url(httpretty.GET, path, data)

    def registry_post(self, path, data):
        self._registry_url(httpretty.POST, path, data)

    @staticmethod
    def _registry_url(method, path, data):
        assert httpretty.is_enabled() is True

        httpretty.register_uri(
            method=method,
            uri=f'{GL_API_URL}/{path}',
            body=json.dumps(data),
            adding_headers={'Content-Type': 'application/json'}
        )


activate_httpretty = partial(httpretty.activate, allow_net_connect=False)
