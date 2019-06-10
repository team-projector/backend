import httpretty

from django.conf import settings
from django.test import override_settings

from apps.core.gitlab import get_gitlab_client
from apps.development.services.gitlab.projects import load_project, load_group_projects
from apps.development.models import Project

from tests.test_development.mocks import GlMocker
from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories_gitlab import AttrDict, GlUserFactory, GlGroupFactory, GlProjectFactory


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@httpretty.activate
def test_load_project(db):
    assert settings.GITLAB_CHECK_WEBHOOKS is False

    group = ProjectGroupFactory.create()
    gl_project = AttrDict(GlProjectFactory())

    mocker = GlMocker()
    mocker.registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())

    gl = get_gitlab_client()

    load_project(gl, group, gl_project)

    project = Project.objects.first()

    _check_project(project, gl_project, group)

    mocker.disable_url()


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@httpretty.activate
def test_load_project(db):
    assert settings.GITLAB_CHECK_WEBHOOKS is False

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)

    mocker = GlMocker()
    mocker.registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    mocker.registry_get_gl_url(f'https://gitlab.com/api/v4/groups/{group.gl_id}', gl_group)

    load_group_projects(group)

    project = Project.objects.first()

    _check_project(project, None, group)

    mocker.disable_url()


def _check_project(project, gl_project, group=None):
    assert project.gl_id == gl_project.id
    assert project.gl_url == gl_project.web_url
    assert project.title == gl_project.name
    assert project.full_title == gl_project.name_with_namespace

    if not group:
        assert project.group is None
    else:
        assert project.group == group
