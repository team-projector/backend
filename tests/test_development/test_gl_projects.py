import pytest
from gitlab.exceptions import GitlabGetError

from rest_framework import status
from django.conf import settings
from django.test import override_settings

from apps.core.gitlab import get_gitlab_client
from apps.development.models import Project
from apps.development.services.gitlab.projects import (
    load_project, load_group_projects, load_projects
)
from tests.test_development.checkers_gitlab import check_project
from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlUserFactory, GlGroupFactory, GlProjectFactory, GlHookFactory)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_project(db, gl_mocker):
    assert settings.GITLAB_CHECK_WEBHOOKS is False

    group = ProjectGroupFactory.create()
    gl_project = AttrDict(GlProjectFactory())

    gl_mocker.registry_get('/user', GlUserFactory())

    gl = get_gitlab_client()

    load_project(gl, group, gl_project)

    project = Project.objects.first()

    check_project(project, gl_project, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN',
                   GITLAB_CHECK_WEBHOOKS=True,
                   DOMAIN_NAME='test.com')
def test_load_project_with_check_webhooks(db, gl_mocker):
    group = ProjectGroupFactory.create()
    gl_project = AttrDict(GlProjectFactory())
    gl_hook_1 = AttrDict(GlHookFactory(url='https://test.com/api/gl-webhook'))
    gl_hook_2 = AttrDict(GlHookFactory(url='https://test1.com/api/1'))

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/hooks', [gl_hook_1])

    gl = get_gitlab_client()

    load_project(gl, group, gl_project)

    project = Project.objects.first()

    check_project(project, gl_project, group)

    gl_mocker.registry_get(f'/projects/{gl_project.id}/hooks', [gl_hook_2])
    gl_mocker.registry_post(f'/projects/{gl_project.id}/hooks', {'id': gl_project.id})

    load_project(gl, group, gl_project)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_group_projects(db, gl_mocker):
    assert settings.GITLAB_CHECK_WEBHOOKS is False

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)

    gl_project_1 = AttrDict(GlProjectFactory())
    gl_project_2 = AttrDict(GlProjectFactory())

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)
    gl_mocker.registry_get(f'/groups/{gl_group.id}/projects',
                           [gl_project_1, gl_project_2])

    load_group_projects(group)

    project = Project.objects.get(gl_id=gl_project_1.id)
    check_project(project, gl_project_1, group)

    project = Project.objects.get(gl_id=gl_project_2.id)
    check_project(project, gl_project_2, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_projects(db, gl_mocker):
    assert settings.GITLAB_CHECK_WEBHOOKS is False

    gl_group_1 = AttrDict(GlGroupFactory())
    group_1 = ProjectGroupFactory.create(gl_id=gl_group_1.id)
    gl_group_2 = AttrDict(GlGroupFactory())
    group_2 = ProjectGroupFactory.create(gl_id=gl_group_2.id)

    gl_project_1 = AttrDict(GlProjectFactory())
    gl_project_2 = AttrDict(GlProjectFactory())

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/groups/{gl_group_1.id}', gl_group_1)
    gl_mocker.registry_get(f'/groups/{gl_group_1.id}/projects', [gl_project_1])
    gl_mocker.registry_get(f'/groups/{gl_group_2.id}', gl_group_2)
    gl_mocker.registry_get(f'/groups/{gl_group_2.id}/projects', [gl_project_2])

    load_projects()

    project = Project.objects.get(gl_id=gl_project_1.id)
    check_project(project, gl_project_1, group_1)

    project = Project.objects.get(gl_id=gl_project_2.id)
    check_project(project, gl_project_2, group_2)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_group_projects_server_error(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}',
                           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    with pytest.raises(GitlabGetError):
        load_group_projects(group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_group_projects_not_found(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}',
                           status_code=status.HTTP_404_NOT_FOUND)

    load_group_projects(group)
