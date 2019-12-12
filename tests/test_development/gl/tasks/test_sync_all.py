from django.test import override_settings

from apps.development.tasks import sync_all_task
from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories_gitlab import (
    AttrDict,
    GlGroupFactory,
    GlIssueFactory,
    GlMergeRequestFactory,
    GlProjectFactory,
    GlProjectMilestoneFactory,
    GlTimeStats,
    GlUserFactory,
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_all_task(db, gl_mocker):
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

    gl_issue = AttrDict(GlIssueFactory(
        project_id=gl_project.id,
        assignee=gl_user,
    ))
    _registry_issue(gl_mocker, gl_project, gl_issue)

    gl_merge_request = AttrDict(GlMergeRequestFactory(
        project_id=gl_project.id,
        assignee=gl_user,
        author=gl_user,
    ))
    _registry_merge_request(gl_mocker, gl_project, gl_merge_request)

    sync_all_task()


def _registry_merge_request(gl_mocker, gl_project, gl_merge_request):
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests',
                           [gl_merge_request])
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}',
        gl_merge_request)
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/time_stats',
        GlTimeStats())
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/closed_by',
        [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/notes',
        [])
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/participants',
        [])


def _registry_issue(gl_mocker, gl_project, gl_issue):
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues', [gl_issue])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}',
                           gl_issue)
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/time_stats',
        GlTimeStats())
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [])
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants', [])
