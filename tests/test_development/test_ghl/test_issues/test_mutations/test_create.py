from datetime import datetime

from apps.development.models import Issue
from tests.test_development.factories.gitlab import (
    GlIssueFactory,
    GlProjectFactory,
)
from tests.test_users.factories.gitlab import GlUserFactory


def test_raw_query(user, project, ghl_client, gl_mocker, ghl_raw):
    """Test raw query."""
    estimate = 500
    user.gl_token = "token"
    user.save()

    gl_mocker.register_get(
        "/projects/{0}".format(project.gl_id),
        _gl_project_response(project),
    )

    issue_data = _gl_issue_response(project, user)

    gl_mocker.register_post(
        "/projects/{0}/issues".format(project.gl_id),
        issue_data,
    )

    gl_mocker.register_post(
        "/projects/{0}/issues/{1}/time_estimate".format(
            project.gl_id,
            issue_data["iid"],
        ),
        {},
    )

    gl_mocker.register_get(
        "/issues/{0}".format(issue_data["id"]),
        issue_data,
    )

    gl_mocker.register_get(
        "/projects/{0}/issues/{1}/time_stats".format(
            project.gl_id,
            issue_data["iid"],
        ),
        _gl_time_stats(estimate),
    )

    gl_mocker.register_get(
        "/projects/{0}/labels".format(project.gl_id),
        [],
    )

    gl_mocker.register_get(
        "/projects/{0}/issues/{1}/notes".format(
            project.gl_id,
            issue_data["iid"],
        ),
        [],
    )

    ghl_client.set_user(user)

    response = ghl_client.execute(
        ghl_raw("create_issue"),
        variable_values={
            "title": "Test issue",
            "project": project.pk,
            "developer": user.pk,
            "estimate": estimate,
            "dueDate": str(datetime.now().date()),
            "milestone": None,
            "labels": [],
        },
    )

    assert "errors" not in response

    issue = Issue.objects.filter(gl_id=issue_data["id"]).first()

    assert issue is not None
    assert issue.title == issue_data["title"]
    assert issue.time_estimate == estimate
    assert issue.project == project


def _gl_time_stats(estimate):
    return {
        "human_time_estimate": "{0}s".format(estimate),
        "human_total_time_spent": "",
        "time_estimate": estimate,
        "total_time_spent": 0,
    }


def _gl_user_response(user):
    return GlUserFactory.create(
        id=user.gl_id,
        name=user.name,
        public_email=user.email,
        username=user.login,
        avatar_url=user.gl_avatar,
        web_url=user.gl_url,
    )


def _gl_issue_response(project, user):
    return GlIssueFactory.create(
        project_id=project.gl_id,
        assignee=_gl_user_response(user),
        milestone=None,
    )


def _gl_project_response(project):
    return GlProjectFactory.create(
        id=project.gl_id,
        name=project.title,
        web_url=project.gl_url,
        avatar_url=project.gl_avatar,
        archived=False,
    )
