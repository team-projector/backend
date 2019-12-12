import pytest
from django.conf import settings
from django.test import override_settings
from gitlab.exceptions import GitlabGetError
from rest_framework import status
from tests.test_development.checkers_gitlab import check_project
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
)
from tests.test_development.factories_gitlab import (
    AttrDict,
    GlGroupFactory,
    GlHookFactory,
    GlProjectFactory,
    GlUserFactory,
)

from apps.development.models import Project
from apps.development.services.project.gl.manager import ProjectGlManager
from apps.development.services.project.gl.provider import ProjectGlProvider


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_project(db, gl_mocker):
    assert settings.GITLAB_CHECK_WEBHOOKS is False

    group = ProjectGroupFactory.create()
    gl_project = AttrDict(GlProjectFactory())

    gl_mocker.registry_get('/user', GlUserFactory())
    ProjectGlManager().update_project(group, gl_project)

    assert Project.objects.count() == 1
    project = Project.objects.first()

    check_project(project, gl_project, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_project_bad(db, gl_mocker):
    assert settings.GITLAB_CHECK_WEBHOOKS is False

    group = ProjectGroupFactory.create()
    gl_project = AttrDict(GlProjectFactory(id='bad_gl_id'))

    gl_mocker.registry_get('/user', GlUserFactory())

    ProjectGlManager().update_project(group, gl_project)

    assert Project.objects.count() == 0


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN',
                   GITLAB_CHECK_WEBHOOKS=True,
                   DOMAIN_NAME='test.com')
def test_load_project_with_check_webhooks(db, gl_mocker, gl_client):
    group = ProjectGroupFactory.create()
    gl_project = AttrDict(GlProjectFactory())
    gl_hook_1 = AttrDict(
        GlHookFactory(url='https://test.com/api/gl_client-webhook'))
    gl_hook_2 = AttrDict(GlHookFactory(url='https://test1.com/api/1'))

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/hooks', [gl_hook_1])
    gl_mocker.registry_post(f'/projects/{gl_project.id}/hooks', {
        'id': gl_project.id
    })
    gl_mocker.registry_delete(f'/projects/{gl_project.id}/hooks')

    gl_project_loaded = gl_client.projects.get(id=gl_project.id)

    ProjectGlManager().update_project(group, gl_project_loaded)

    project = Project.objects.first()

    check_project(project, gl_project, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_group_projects(db, gl_mocker, gl_client):
    assert settings.GITLAB_CHECK_WEBHOOKS is False

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)

    gl_project_1 = AttrDict(GlProjectFactory())
    gl_project_2 = AttrDict(GlProjectFactory())

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)
    gl_mocker.registry_get(f'/groups/{gl_group.id}/projects',
                           [gl_project_1, gl_project_2])

    ProjectGlManager().sync_group_projects(group)

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

    ProjectGlManager().sync_all_projects()

    project = Project.objects.get(gl_id=gl_project_1.id)
    check_project(project, gl_project_1, group_1)

    project = Project.objects.get(gl_id=gl_project_2.id)
    check_project(project, gl_project_2, group_2)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_deactivate_if_not_found(db, gl_mocker):
    project = ProjectFactory()

    assert project.is_active

    gl_mocker.registry_get(
        f'/projects/{project.gl_id}',
        status_code=status.HTTP_404_NOT_FOUND,
    )

    ProjectGlProvider().get_gl_project(project)

    project.refresh_from_db()

    assert not project.is_active


def test_for_sync(db, gl_mocker):
    ProjectFactory()

    assert Project.objects.for_sync().count() == 1


def test_for_sync_but_inactive(db, gl_mocker):
    ProjectFactory(is_active=False)

    assert Project.objects.for_sync().count() == 0


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_group_projects_server_error(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}',
                           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    with pytest.raises(GitlabGetError):
        ProjectGlManager().sync_group_projects(group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_group_projects_not_found(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}',
                           status_code=status.HTTP_404_NOT_FOUND)

    ProjectGlManager().sync_group_projects(group)
