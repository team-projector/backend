from django.test import override_settings

from apps.development.models import Milestone
from apps.development.services.gitlab.milestones import (
    load_group_milestone, load_project_milestone, load_group_milestones, load_gl_project_milestones
)
from tests.test_development.factories import ProjectFactory, ProjectGroupFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlUserFactory, GlGroupFactory, GlProjectFactory, GlProjectMilestoneFactory,
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_group_milestone(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}/milestones/{gl_milestone.id}', gl_milestone)

    load_group_milestone(group, gl_group.id, gl_milestone.id)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    _check_milestone(milestone, gl_milestone, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_project_milestone(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/milestones/{gl_milestone.id}', gl_milestone)

    load_project_milestone(project, gl_project.id, gl_milestone.id)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    _check_milestone(milestone, gl_milestone, project)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_group_milestones(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}/milestones', [gl_milestone])

    load_group_milestones(group.id, gl_group.id)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    _check_milestone(milestone, gl_milestone, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_gl_project_milestones(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlGroupFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/milestones', [gl_milestone])

    load_gl_project_milestones(project.id, gl_project.id)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    _check_milestone(milestone, gl_milestone, project)


def _check_milestone(milestone, gl_milestone, owner):
    assert milestone.gl_id == gl_milestone.id
    assert milestone.gl_iid == gl_milestone.iid
    assert milestone.gl_url == gl_milestone.web_url
    assert milestone.title == gl_milestone.title
    assert milestone.description == gl_milestone.description
    assert milestone.start_date is not None
    assert milestone.due_date is not None
    assert milestone.created_at is not None
    assert milestone.updated_at is not None
    assert milestone.state == gl_milestone.state
    assert milestone.owner == owner
