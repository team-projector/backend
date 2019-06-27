from django.test import override_settings

from apps.core.gitlab import get_gitlab_client
from apps.development.models import Issue, Note
from apps.development.services.gitlab.issues import (
    load_issue_participants, load_issue_notes, load_issue_labels, load_project_issue, load_issues
)
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlUserFactory, GlProjectFactory, GlProjectsIssueFactory, GlIssueNoteFactory, GlLabelFactory,
    GlIssueTimeStats
)
from tests.test_development.mocks import activate_httpretty, registry_get_gl_url


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate_httpretty
def test_load_issue_participants(db):
    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)

    gl_issue = AttrDict(GlProjectsIssueFactory())
    issue = IssueFactory.create(gl_id=gl_issue.id, gl_iid=gl_issue.iid, project=project)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)

    gl_participant_1 = AttrDict(GlUserFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/users/{gl_participant_1.id}', gl_participant_1)

    gl_participant_2 = AttrDict(GlUserFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/users/{gl_participant_2.id}', gl_participant_2)

    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}'
                        f'/participants', [gl_participant_1, gl_participant_2])

    gl_project = gl.projects.get(id=project.gl_id)
    gl_issue = gl_project.issues.get(id=issue.gl_iid)

    load_issue_participants(issue, gl_issue)

    participant_1 = issue.participants.get(login=gl_participant_1.username)
    participant_2 = issue.participants.get(login=gl_participant_2.username)

    _check_user(participant_1, gl_participant_1)
    _check_user(participant_2, gl_participant_2)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate_httpretty
def test_load_issue_notes(db):
    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)

    gl_issue = AttrDict(GlProjectsIssueFactory(project_id=gl_project.id))
    issue = IssueFactory.create(gl_id=gl_issue.id, gl_iid=gl_issue.iid, project=project)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)

    gl_author = AttrDict(GlUserFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/users/{gl_author.id}', gl_author)

    gl_note = AttrDict(GlIssueNoteFactory(author=gl_author, body='added 1h of time spent at 2000-01-01'))
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [gl_note])

    gl_project = gl.projects.get(id=project.gl_id)
    gl_issue = gl_project.issues.get(id=issue.gl_iid)

    load_issue_notes(issue, gl_issue)

    note = issue.notes.first()

    assert note.gl_id == gl_note.id
    assert note.type == Note.TYPE.time_spend
    assert note.body == 'added 1h of time spent at 2000-01-01'
    assert note.created_at is not None
    assert note.updated_at is not None
    assert note.user.login == gl_author.username
    assert note.content_object == issue
    assert note.data == {'date': '2000-01-01', 'spent': 3600}
    _check_user(note.user, gl_author)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate_httpretty
def test_load_issue_labels(db):
    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)

    gl_label = AttrDict(GlLabelFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/labels', [gl_label])

    gl_issue = AttrDict(GlProjectsIssueFactory(project_id=gl_project.id), labels=[gl_label])
    issue = IssueFactory.create(gl_id=gl_issue.id, gl_iid=gl_issue.iid, project=project)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)

    gl_project = gl.projects.get(id=project.gl_id)
    gl_issue = gl_project.issues.get(id=issue.gl_iid)

    load_issue_labels(issue, gl_project, gl_issue)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate_httpretty
def test_load_project_issue(db):
    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)

    gl_assignee = AttrDict(GlUserFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/users/{gl_assignee.id}', gl_assignee)

    gl_issue = AttrDict(GlProjectsIssueFactory(project_id=gl_project.id, assignee=gl_assignee, state='closed'))
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}'
                        f'/time_stats', GlIssueTimeStats())
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', [])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/labels', [])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}'
                        f'/participants', [])

    gl_project_load = gl.projects.get(id=project.gl_id)
    gl_issue_load = gl_project_load.issues.get(id=gl_issue.iid)

    load_project_issue(project, gl_project_load, gl_issue_load)

    issue = Issue.objects.first()

    _check_issue(issue, gl_issue)
    _check_user(issue.user, gl_assignee)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate_httpretty
def test_load_issues(db):
    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)

    gl_assignee = AttrDict(GlUserFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/users/{gl_assignee.id}', gl_assignee)

    gl_issue = AttrDict(GlProjectsIssueFactory(project_id=gl_project.id, assignee=gl_assignee))
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues', [gl_issue])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}'
                        f'/time_stats', GlIssueTimeStats())
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', [])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/labels', [])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/issues/{gl_issue.iid}'
                        f'/participants', [])

    load_issues()

    issue = Issue.objects.first()

    _check_issue(issue, gl_issue)
    _check_user(issue.user, gl_assignee)


def _check_issue(issue, gl_issue):
    assert issue.gl_id == gl_issue.id
    assert issue.gl_iid == gl_issue.iid
    assert issue.gl_url == gl_issue.web_url
    assert issue.title == gl_issue.title
    assert issue.state == gl_issue.state
    assert issue.created_at is not None
    assert issue.updated_at is not None


def _check_user(user, gl_user):
    assert user.login == gl_user.username
    assert user.name == gl_user.name
    assert user.gl_avatar == gl_user.avatar_url
    assert user.gl_url == gl_user.web_url
