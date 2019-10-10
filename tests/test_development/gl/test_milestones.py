from django.test import override_settings

from apps.development.models import Milestone
from apps.development.services import milestone as milestone_service
from tests.test_development.checkers_gitlab import check_milestone
from tests.test_development.factories import (
    ProjectFactory, ProjectGroupFactory
)
from tests.test_development.factories_gitlab import (
    AttrDict, GlUserFactory, GlGroupFactory, GlProjectFactory,
    GlProjectMilestoneFactory,
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_project_group_milestone(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}/milestones'
                           f'/{gl_milestone.id}', gl_milestone)

    milestone_service.load_for_project_group(group, gl_group.id, gl_milestone.id)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    check_milestone(milestone, gl_milestone, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_for_project(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/milestones'
                           f'/{gl_milestone.id}', gl_milestone)

    milestone_service.load_for_project(project, gl_project.id, gl_milestone.id)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    check_milestone(milestone, gl_milestone, project)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_for_project_group_all(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}/milestones',
                           [gl_milestone])

    milestone_service.load_for_project_group_all(group.id, gl_group.id)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    check_milestone(milestone, gl_milestone, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_for_project_all(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlGroupFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/milestones',
                           [gl_milestone])

    milestone_service.load_for_project_all(project.id, gl_project.id)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    check_milestone(milestone, gl_milestone, project)
