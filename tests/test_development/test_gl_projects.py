from django.conf import settings
from django.test import override_settings

from apps.core.gitlab import get_gitlab_client
from apps.development.services.gitlab.projects import load_project, load_group_projects, load_projects
from apps.development.models import Project

from tests.test_development.mocks import activate, registry_get_gl_url, registry_post_gl_url
from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlUserFactory, GlGroupFactory, GlProjectFactory, GlHookFactory)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate
def test_load_project(db):
    assert settings.GITLAB_CHECK_WEBHOOKS is False

    group = ProjectGroupFactory.create()
    gl_project = AttrDict(GlProjectFactory())

    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())

    gl = get_gitlab_client()

    load_project(gl, group, gl_project)

    project = Project.objects.first()

    _check_project(project, gl_project, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN',
                   GITLAB_CHECK_WEBHOOKS=True,
                   DOMAIN_NAME='test.com')
@activate
def test_load_project_with_check_webhooks(db):
    group = ProjectGroupFactory.create()
    gl_project = AttrDict(GlProjectFactory())
    gl_hook_1 = AttrDict(GlHookFactory(url='https://test.com/api/gl-webhook'))
    gl_hook_2 = AttrDict(GlHookFactory(url='https://test1.com/api/1'))

    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/hooks', [gl_hook_1])

    gl = get_gitlab_client()

    load_project(gl, group, gl_project)

    project = Project.objects.first()

    _check_project(project, gl_project, group)

    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/hooks', [gl_hook_2])
    registry_post_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/hooks', {'id': gl_project.id})

    load_project(gl, group, gl_project)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate
def test_load_group_projects(db):
    assert settings.GITLAB_CHECK_WEBHOOKS is False

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)

    gl_project_1 = AttrDict(GlProjectFactory())
    gl_project_2 = AttrDict(GlProjectFactory())

    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/groups/{gl_group.id}', gl_group)
    registry_get_gl_url(f'https://gitlab.com/api/v4/groups/{gl_group.id}/projects', [gl_project_1, gl_project_2])

    load_group_projects(group)

    project = Project.objects.get(gl_id=gl_project_1.id)
    _check_project(project, gl_project_1, group)

    project = Project.objects.get(gl_id=gl_project_2.id)
    _check_project(project, gl_project_2, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate
def test_load_projects(db):
    assert settings.GITLAB_CHECK_WEBHOOKS is False

    gl_group_1 = AttrDict(GlGroupFactory())
    group_1 = ProjectGroupFactory.create(gl_id=gl_group_1.id)
    gl_group_2 = AttrDict(GlGroupFactory())
    group_2 = ProjectGroupFactory.create(gl_id=gl_group_2.id)

    gl_project_1 = AttrDict(GlProjectFactory())
    gl_project_2 = AttrDict(GlProjectFactory())

    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/groups/{gl_group_1.id}', gl_group_1)
    registry_get_gl_url(f'https://gitlab.com/api/v4/groups/{gl_group_1.id}/projects', [gl_project_1])
    registry_get_gl_url(f'https://gitlab.com/api/v4/groups/{gl_group_2.id}', gl_group_2)
    registry_get_gl_url(f'https://gitlab.com/api/v4/groups/{gl_group_2.id}/projects', [gl_project_2])

    load_projects()

    project = Project.objects.get(gl_id=gl_project_1.id)
    _check_project(project, gl_project_1, group_1)

    project = Project.objects.get(gl_id=gl_project_2.id)
    _check_project(project, gl_project_2, group_2)


def _check_project(project, gl_project, group=None):
    assert project.gl_id == gl_project.id
    assert project.gl_url == gl_project.web_url
    assert project.title == gl_project.name
    assert project.full_title == gl_project.name_with_namespace

    if not group:
        assert project.group is None
    else:
        assert project.group == group
