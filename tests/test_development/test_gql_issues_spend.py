from pytest import raises
from django.test import override_settings
from rest_framework.exceptions import ValidationError

from apps.development.graphql.mutations.issues import AddSpendIssueMutation
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlIssueFactory, GlIssueAddSpentTimeFactory, GlProjectFactory,
    GlUserFactory
)


def test_user_without_gl_token(user, client):
    issue = IssueFactory.create(user=user)

    client.user = user
    info = AttrDict({'context': client})

    with raises(ValidationError):
        AddSpendIssueMutation.do_mutate(
            None, info, issue.id, 60
        )


def test_bad_time(user, client):
    user.gl_token = 'token'
    user.save()

    issue = IssueFactory.create(user=user)

    client.user = user
    info = AttrDict({'context': client})

    with raises(ValidationError):
        AddSpendIssueMutation.do_mutate(
            None, info, issue.id, -30
        )


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_spend(user, client, gl_mocker):
    user.gl_token = 'token'
    user.save()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)

    gl_project_issue = AttrDict(GlIssueFactory(id=gl_project.id))
    issue = IssueFactory.create(
        gl_iid=gl_project_issue.iid,
        user=user,
        project=project
    )

    IssueFactory.create_batch(5, project=project)

    gl_mocker.registry_get(
        '/user',
        GlUserFactory()
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}',
        gl_project
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_project_issue.iid}',
        gl_project_issue
    )
    gl_mocker.registry_post(
        f'/projects/{gl_project.id}/issues/{gl_project_issue.iid}'
        f'/add_spent_time',
        GlIssueAddSpentTimeFactory())

    client.user = user
    info = AttrDict({'context': client})

    issue_spend = AddSpendIssueMutation.do_mutate(
        None, info, issue.id, 60
    ).issue

    assert issue_spend == issue
