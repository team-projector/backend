import json

from rest_framework import status

from tests.base import HttpPrettyTests
from tests.test_development.factories_gitlab import (
    GlUserFactory, GlProjectFactory, GlProjectsIssueFactory, GlIssueAddSpentTimeFactory)


class BaseGitlabMockTests(HttpPrettyTests):
    def registry_user(self, **kwargs) -> None:
        url = 'https://gitlab.com/api/v4/user'
        self._registry_get_gl_url(url, GlUserFactory(**kwargs))

    def registry_project(self, project_id: int, **kwargs) -> None:
        url = f'https://gitlab.com/api/v4/projects/{project_id}'
        self._registry_get_gl_url(url, GlProjectFactory(id=project_id, **kwargs))

    def registry_project_issue(self, project_id: int, issue_id: int, **kwargs) -> None:
        url = f'https://gitlab.com/api/v4/projects/{project_id}/issues/{issue_id}'
        self._registry_get_gl_url(url, GlProjectsIssueFactory(id=project_id, iid=issue_id, **kwargs))

    def registry_issue_add_spent_time(self, project_id: int, issue_id: int) -> None:
        url = f'https://gitlab.com/api/v4/projects/{project_id}/issues/{issue_id}/add_spent_time'
        self._registry_post_gl_url(url, GlIssueAddSpentTimeFactory())

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
