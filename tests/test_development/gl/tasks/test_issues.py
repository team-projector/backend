from django.test import override_settings

from apps.development.models import Issue
from apps.development.tasks import sync_issues_task
from tests.test_development.checkers_gitlab import check_issue
from tests.test_development.factories import ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict,
    GlIssueFactory,
    GlProjectFactory,
    GlTimeStats,
    GlUserFactory,
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_issues_task(db, gl_mocker):
    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_assignee = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_assignee.id}', gl_assignee)

    gl_issue = AttrDict(GlIssueFactory(
        project_id=gl_project.id,
        assignee=gl_assignee,
    ))
    _registry_issue(gl_mocker, gl_project, gl_issue)

    sync_issues_task()

    issue = Issue.objects.first()

    check_issue(issue, gl_issue)


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
