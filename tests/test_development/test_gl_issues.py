import pytest
from gitlab.exceptions import GitlabGetError

from rest_framework import status
from django.test import override_settings
from django.utils import timezone

from apps.core.gitlab import get_gitlab_client
from apps.development.models import Issue, Note
from apps.development.services.gitlab.issues import (
    load_issue_participants, load_issue_notes, load_issue_labels, load_project_issue, load_issues, load_project_issues,
    check_projects_deleted_issues
)
from tests.test_development.factories import IssueFactory, ProjectFactory, ProjectMilestoneFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlUserFactory, GlProjectFactory, GlProjectsIssueFactory, GlIssueNoteFactory, GlLabelFactory,
    GlProjectMilestoneFactory, GlIssueTimeStats
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_issue_participants(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_issue = AttrDict(GlProjectsIssueFactory())
    issue = IssueFactory.create(gl_id=gl_issue.id, gl_iid=gl_issue.iid, project=project)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)

    gl_participant_1 = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_participant_1.id}', gl_participant_1)

    gl_participant_2 = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_participant_2.id}', gl_participant_2)

    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants',
                           [gl_participant_1, gl_participant_2])

    gl_project = gl.projects.get(id=project.gl_id)
    gl_issue = gl_project.issues.get(id=issue.gl_iid)

    load_issue_participants(issue, gl_issue)

    participant_1 = issue.participants.get(login=gl_participant_1.username)
    participant_2 = issue.participants.get(login=gl_participant_2.username)

    _check_user(participant_1, gl_participant_1)
    _check_user(participant_2, gl_participant_2)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_issue_notes(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_issue = AttrDict(GlProjectsIssueFactory(project_id=gl_project.id))
    issue = IssueFactory.create(gl_id=gl_issue.id, gl_iid=gl_issue.iid, project=project)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)

    gl_author = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_author.id}', gl_author)

    gl_note = AttrDict(GlIssueNoteFactory(author=gl_author, body='added 1h of time spent at 2000-01-01'))
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [gl_note])

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
def test_load_issue_labels(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_label = AttrDict(GlLabelFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [gl_label])

    gl_issue = AttrDict(GlProjectsIssueFactory(project_id=gl_project.id), labels=[gl_label.name])
    issue = IssueFactory.create(gl_id=gl_issue.id, gl_iid=gl_issue.iid, project=project)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)

    gl_project_loaded = gl.projects.get(id=project.gl_id)
    gl_issue_loaded = gl_project_loaded.issues.get(id=issue.gl_iid)

    load_issue_labels(issue, gl_project_loaded, gl_issue_loaded)

    issue = Issue.objects.first()

    assert issue.gl_id == gl_issue.id
    assert issue.labels.first().title == gl_label.name


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_project_issue(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_assignee = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_assignee.id}', gl_assignee)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    milestone = ProjectMilestoneFactory.create(gl_id=gl_milestone.id)

    gl_issue = AttrDict(GlProjectsIssueFactory(project_id=gl_project.id, assignee=gl_assignee,
                                               state='closed', milestone=gl_milestone))
    _registry_issue(gl_mocker, gl_project, gl_issue)

    gl_project_loaded = gl.projects.get(id=project.gl_id)
    gl_issue_loaded = gl_project_loaded.issues.get(id=gl_issue.iid)

    load_project_issue(project, gl_project_loaded, gl_issue_loaded)

    issue = Issue.objects.first()

    _check_issue(issue, gl_issue)
    _check_user(issue.user, gl_assignee)
    assert issue.milestone == milestone


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_project_issues(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id,
                                    gl_last_issues_sync=timezone.now() - timezone.timedelta(days=10))
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_assignee = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_assignee.id}', gl_assignee)

    gl_issue = AttrDict(GlProjectsIssueFactory(project_id=gl_project.id, assignee=gl_assignee))
    _registry_issue(gl_mocker, gl_project, gl_issue)

    load_project_issues(project, check_deleted=False)

    issue = Issue.objects.first()

    _check_issue(issue, gl_issue)

    project.refresh_from_db()
    assert timezone.datetime.date(project.gl_last_issues_sync) == timezone.now().date()


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_issues(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_assignee = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_assignee.id}', gl_assignee)

    gl_issue = AttrDict(GlProjectsIssueFactory(project_id=gl_project.id, assignee=gl_assignee))
    _registry_issue(gl_mocker, gl_project, gl_issue)

    load_issues()

    issue = Issue.objects.first()

    _check_issue(issue, gl_issue)
    _check_user(issue.user, gl_assignee)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_issues_server_error(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    with pytest.raises(GitlabGetError):
        load_issues()


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_issues_not_found(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', status_code=status.HTTP_404_NOT_FOUND)

    load_issues()


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_check_projects_deleted_issues(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_assignee = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_assignee.id}', gl_assignee)

    gl_issue = AttrDict(GlProjectsIssueFactory(project_id=gl_project.id, assignee=gl_assignee))
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues', [gl_issue])

    IssueFactory.create_batch(5, project=project)

    check_projects_deleted_issues()


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_check_projects_deleted_issues_server_error(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    with pytest.raises(GitlabGetError):
        load_issues()


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_check_projects_deleted_issues_not_found(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', status_code=status.HTTP_404_NOT_FOUND)

    check_projects_deleted_issues()


def _registry_issue(gl_mocker, gl_project, gl_issue):
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues', [gl_issue])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/time_stats', GlIssueTimeStats())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants', [])


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
