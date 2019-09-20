from apps.development.models import Project
from tests.base import model_admin
from tests.test_development.factories import (
    ProjectGroupFactory, ProjectFactory
)
from tests.test_development.factories_gitlab import (
    AttrDict, GlGroupFactory, GlProjectFactory, GlUserFactory,
)


def test_sync_handler(db, gl_mocker):
    ma_project = model_admin(Project)

    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_project = AttrDict(GlProjectFactory(name='update'))
    project = ProjectFactory.create(gl_id=gl_project.id, group=group, title='created')
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    assert project.title == 'created'

    ma_project.sync_handler(project)

    project = Project.objects.first()

    assert project.title == 'update'
