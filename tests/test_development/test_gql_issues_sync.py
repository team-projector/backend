from django.test import override_settings

from apps.development.graphql.mutations.issues import SyncIssueMutation
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlTimeStats, GlUserFactory, GlProjectFactory,
    GlIssueFactory
)
from tests.test_users.factories import UserFactory


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project(user, client, gl_mocker):
    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)

    gl_assignee = AttrDict(GlUserFactory())
    UserFactory.create(gl_id=gl_assignee.id)

    gl_issue = AttrDict(GlIssueFactory(
        project_id=gl_project.id,
        assignee=gl_assignee,
        state='closed'
    ))

    issue = IssueFactory.create(
        user=user,
        gl_id=gl_issue.id,
        gl_iid=gl_issue.iid,
        project=project,
        state='opened'
    )

    gl_mocker.registry_get(
        '/user', GlUserFactory()
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}',
        gl_project
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}',
        gl_issue
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/time_stats',
        GlTimeStats()
    )
    gl_mocker.registry_get(
        f'/users/{gl_assignee.id}',
        gl_assignee
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', []
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/labels', []
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', []
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants', []
    )

    assert issue.state == 'opened'

    client.user = user
    info = AttrDict({
        'context': client
    })

    issue_mutated = SyncIssueMutation().do_mutate(None, info, issue.id).issue

    assert issue_mutated.id == issue.id
    assert issue_mutated.gl_id == issue.gl_id

    issue.refresh_from_db()
    assert issue.state == 'closed'
