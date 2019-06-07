import json

from rest_framework import status

from tests.base import HttpPrettyTests
from tests.test_development.factories import (
    gl_user_factory, gl_project_factory, gl_project_issues_factory, gl_issue_add_spent_time_factory)

PATH_GL_API = 'https://gitlab.com/api/v4'


class BaseGitlabMockTests(HttpPrettyTests):
    def registry_user(self) -> None:
        url = f'{PATH_GL_API}/user'
        self._registry_get_gl_url(url, gl_user_factory())

    def registry_project(self, project_id: int) -> None:
        url = f'{PATH_GL_API}/projects/{project_id}'
        self._registry_get_gl_url(url, gl_project_factory(project_id))

    def registry_project_issue(self, project_id: int, issue_id: int) -> None:
        url = f'{PATH_GL_API}/projects/{project_id}/issues/{issue_id}'
        self._registry_get_gl_url(url, gl_project_issues_factory(project_id, issue_id))

    def registry_issue_add_spent_time(self, project_id: int, issue_id: int) -> None:
        url = f'{PATH_GL_API}/projects/{project_id}/issues/{issue_id}/add_spent_time'
        self._registry_post_gl_url(url, gl_issue_add_spent_time_factory())

    def _registry_get_gl_url(self, url: str, factory: dict) -> None:
        def request_callback(request, uri, response_headers):
            response_headers['Content-Type'] = 'application/json'
            data = json.dumps(factory)

            return [status.HTTP_200_OK, response_headers, data]

        self.registry_get_url(url, status.HTTP_200_OK, body=request_callback)

    def _registry_post_gl_url(self, url: str, factory: dict) -> None:
        def request_callback(request, uri, response_headers):
            response_headers['Content-Type'] = 'application/json'
            data = json.dumps(factory)

            return [status.HTTP_200_OK, response_headers, data]

        self.registry_post_url(url, status.HTTP_200_OK, body=request_callback)
