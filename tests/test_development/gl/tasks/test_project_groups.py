from django.test import override_settings

from apps.development.models import ProjectGroup
from apps.development.tasks import sync_project_group_task
from tests.test_development.checkers_gitlab import check_group
from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories_gitlab import (
    AttrDict,
    GlGroupFactory,
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project_group_task(db, gl_mocker):
    gl_group = AttrDict(GlGroupFactory())
    ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    sync_project_group_task(gl_group.id)

    group = ProjectGroup.objects.get(gl_id=gl_group.id)
    check_group(group, gl_group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project_group_with_parent(db, gl_mocker):
    gl_parent = AttrDict(GlGroupFactory())
    parent = ProjectGroupFactory.create(gl_id=gl_parent.id)

    gl_group = AttrDict(GlGroupFactory(parent_id=parent.gl_id))
    ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    sync_project_group_task(gl_group.id)

    group = ProjectGroup.objects.get(gl_id=gl_group.id)
    check_group(group, gl_group, parent)
