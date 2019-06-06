import httpretty

from django.conf import settings
from django.test import override_settings
from django.test import TestCase

from apps.core.gitlab import get_gitlab_client
from apps.development.services.gitlab.projects import load_project
from apps.development.models import Project

from tests.test_development.mocks import BaseGitlabMockTests
from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories_gitlab import GlProjectFactory


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
class GlProjectsTests(TestCase, BaseGitlabMockTests):
    @httpretty.activate
    def test_load_project(self):
        self.assertFalse(settings.GITLAB_CHECK_WEBHOOKS)

        self.registry_user()

        gl = get_gitlab_client()
        group = ProjectGroupFactory()
        gl_project = GlProjectFactory.stub()

        load_project(gl, group, gl_project)

        project = Project.objects.first()

        self.assertTrue(project.gl_id, gl_project.id)
        self.assertTrue(project.gl_url, gl_project.web_url)
        self.assertTrue(project.full_title, gl_project.name_with_namespace)
        self.assertTrue(project.title, gl_project.name)
        self.assertTrue(project.group, group)

        self.disable_url()
