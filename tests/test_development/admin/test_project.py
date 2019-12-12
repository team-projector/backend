from django.test import override_settings
from tests.helpers.base import model_admin
from tests.test_development.checkers_gitlab import check_project
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
)
from tests.test_development.factories_gitlab import (
    AttrDict,
    GlGroupFactory,
    GlProjectFactory,
)

from apps.development.models import Project


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_handler(db, gl_mocker, gl_client):
    # gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id, group=group)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    ma_project = model_admin(Project)
    ma_project.sync_handler(project)

    project = Project.objects.first()

    check_project(project, gl_project, group)
