from django.test import override_settings

from apps.development.models import (
    Issue, Project, ProjectGroup, Milestone, MergeRequest
)
from apps.development.tasks import (
    sync_issues, sync_project_group, sync_project_merge_request,
    sync_merge_requests, sync_projects_milestones, sync_groups_milestones,
    sync_project, sync_user, sync
)
from apps.users.models import User

from tests.test_development.checkers_gitlab import (
    check_group, check_issue, check_milestone, check_merge_request,
    check_project, check_user
)
from tests.test_development.factories import (
    ProjectFactory, ProjectGroupFactory
)
from tests.test_development.factories_gitlab import (
    AttrDict, GlIssueFactory, GlGroupFactory, GlProjectFactory,
    GlProjectMilestoneFactory, GlTimeStats, GlUserFactory,
    GlMergeRequestFactory
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project_group(db, gl_mocker):
    gl_group = AttrDict(GlGroupFactory())

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    sync_project_group(gl_group.id)

    group = ProjectGroup.objects.get(gl_id=gl_group.id)
    check_group(group, gl_group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project_group_with_parent(db, gl_mocker):
    gl_parent = AttrDict(GlGroupFactory())
    parent = ProjectGroupFactory.create(gl_id=gl_parent.id)

    gl_group = AttrDict(GlGroupFactory(parent_id=parent.gl_id))

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    sync_project_group(gl_group.id)

    group = ProjectGroup.objects.get(gl_id=gl_group.id)
    check_group(group, gl_group, parent)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_issues(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_assignee = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_assignee.id}', gl_assignee)

    gl_issue = AttrDict(GlIssueFactory(project_id=gl_project.id, assignee=gl_assignee))
    _registry_issue(gl_mocker, gl_project, gl_issue)

    sync_issues()

    issue = Issue.objects.first()

    check_issue(issue, gl_issue)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project_merge_request(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_user = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id, assignee=gl_user, author=gl_user))
    _registry_merge_request(gl_mocker, gl_project, gl_merge_request)

    sync_project_merge_request(project.gl_id, gl_merge_request.iid)

    merge_request = MergeRequest.objects.first()

    check_merge_request(merge_request, gl_merge_request)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_merge_requests(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_user = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id, assignee=gl_user, author=gl_user))
    _registry_merge_request(gl_mocker, gl_project, gl_merge_request)

    sync_merge_requests()

    merge_request = MergeRequest.objects.first()

    check_merge_request(merge_request, gl_merge_request)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_gl_project_milestones(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlGroupFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/milestones',
                           [gl_milestone])

    sync_projects_milestones()

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    check_milestone(milestone, gl_milestone, project)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_groups_milestones(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}/milestones',
                           [gl_milestone])

    sync_groups_milestones()

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    check_milestone(milestone, gl_milestone, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/milestones',
                           [gl_milestone])

    sync_project(group.id, gl_project.id, project.id)

    project = Project.objects.get(gl_id=gl_project.id)
    check_project(project, gl_project, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_update_users(db, gl_mocker):
    gl_user = AttrDict(GlUserFactory())

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    sync_user(gl_user.id)

    user = User.objects.get(gl_id=gl_user.id)

    check_user(user, gl_user)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get('/groups', [gl_group])
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}/milestones',
                           [gl_milestone])

    gl_project = AttrDict(GlProjectFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}/projects', [gl_project])

    gl_mocker.registry_get(f'/projects/{gl_project.id}/milestones',
                           [gl_milestone])

    gl_user = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    gl_issue = AttrDict(GlIssueFactory(project_id=gl_project.id, assignee=gl_user))
    _registry_issue(gl_mocker, gl_project, gl_issue)

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id, assignee=gl_user, author=gl_user))
    _registry_merge_request(gl_mocker, gl_project, gl_merge_request)

    sync()


def _registry_merge_request(gl_mocker, gl_project, gl_merge_request):
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests', [gl_merge_request])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}', gl_merge_request)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/time_stats', GlTimeStats())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/closed_by', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/notes', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/participants', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/closes_issues', [])


def _registry_issue(gl_mocker, gl_project, gl_issue):
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues', [gl_issue])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/time_stats', GlTimeStats())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants', [])
