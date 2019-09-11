import pytest
from gitlab.exceptions import GitlabGetError

from rest_framework import status
from django.test import override_settings
from django.utils import timezone

from apps.core.gitlab import get_gitlab_client
from apps.development.models import MergeRequest, Note
from apps.development.services.gitlab.merge_requests import (
    load_merge_request_notes, load_merge_request_labels,
    load_project_merge_request, load_merge_requests,
    load_project_merge_requests, load_merge_request_participants
)
from tests.test_development.checkers_gitlab import (
    check_merge_request, check_user
)
from tests.test_development.factories import (
    ProjectFactory, MergeRequestFactory, ProjectMilestoneFactory
)
from tests.test_development.factories_gitlab import (
    AttrDict, GlUserFactory, GlProjectFactory, GlMergeRequestFactory,
    GlNoteFactory, GlLabelFactory, GlTimeStats, GlIssueFactory,
    GlProjectMilestoneFactory,
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_merge_request_participants(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_merge_request = AttrDict(GlMergeRequestFactory())
    merge_request = MergeRequestFactory.create(gl_id=gl_merge_request.id, gl_iid=gl_merge_request.iid, project=project)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}', gl_merge_request)

    gl_participant_1 = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_participant_1.id}', gl_participant_1)

    gl_participant_2 = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_participant_2.id}', gl_participant_2)

    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/participants',
                           [gl_participant_1, gl_participant_2])

    gl_project = gl.projects.get(id=project.gl_id)
    gl_merge_request = gl_project.mergerequests.get(id=merge_request.gl_iid)

    load_merge_request_participants(merge_request, gl_merge_request)

    participant_1 = merge_request.participants.get(login=gl_participant_1.username)
    participant_2 = merge_request.participants.get(login=gl_participant_2.username)

    check_user(participant_1, gl_participant_1)
    check_user(participant_2, gl_participant_2)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_merge_request_notes(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id))
    merge_request = MergeRequestFactory.create(gl_id=gl_merge_request.id, gl_iid=gl_merge_request.iid, project=project)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}', gl_merge_request)

    gl_author = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_author.id}', gl_author)

    gl_note = AttrDict(GlNoteFactory(author=gl_author, body='added 1h of time spent at 2000-01-01'))
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/notes', [gl_note])

    gl_project_loaded = gl.projects.get(id=project.gl_id)
    gl_merge_request_loaded = gl_project_loaded.mergerequests.get(id=merge_request.gl_iid)

    load_merge_request_notes(merge_request, gl_merge_request_loaded)

    note = merge_request.notes.first()

    assert note.gl_id == gl_note.id
    assert note.type == Note.TYPE.time_spend
    assert note.body == 'added 1h of time spent at 2000-01-01'
    assert note.created_at is not None
    assert note.updated_at is not None
    assert note.user.login == gl_author.username
    assert note.content_object == merge_request
    assert note.data == {'date': '2000-01-01', 'spent': 3600}
    check_user(note.user, gl_author)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_merge_request_labels(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_label = AttrDict(GlLabelFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [gl_label])

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id), labels=[gl_label.name])
    merge_request = MergeRequestFactory.create(gl_id=gl_merge_request.id, gl_iid=gl_merge_request.iid, project=project)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}', gl_merge_request)

    gl_project_loaded = gl.projects.get(id=project.gl_id)
    gl_merge_request_loaded = gl_project_loaded.mergerequests.get(id=merge_request.gl_iid)

    load_merge_request_labels(merge_request, gl_project_loaded, gl_merge_request_loaded)

    merge_request = MergeRequest.objects.first()

    assert merge_request.gl_id == gl_merge_request.id
    assert merge_request.labels.first().title == gl_label.name


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_project_merge_request(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_user = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    milestone = ProjectMilestoneFactory.create(gl_id=gl_milestone.id)

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id, assignee=gl_user, author=gl_user,
                                                      state='closed', milestone=gl_milestone))
    _registry_merge_request(gl_mocker, gl_project, gl_merge_request)

    gl_project_loaded = gl.projects.get(id=project.gl_id)
    gl_merge_request_loaded = gl_project_loaded.mergerequests.get(id=gl_merge_request.iid)

    load_project_merge_request(project, gl_project_loaded, gl_merge_request_loaded)

    merge_request = MergeRequest.objects.first()

    check_merge_request(merge_request, gl_merge_request_loaded)
    check_user(merge_request.author, gl_user)
    check_user(merge_request.user, gl_user)
    assert merge_request.milestone == milestone


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_project_merge_requests(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id, gl_last_merge_requests_sync=timezone.now())
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_user = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id, assignee=gl_user, author=gl_user))
    _registry_merge_request(gl_mocker, gl_project, gl_merge_request)

    load_project_merge_requests(project, full_reload=True)

    merge_request = MergeRequest.objects.first()

    check_merge_request(merge_request, gl_merge_request)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_merge_requests(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id,
                                    gl_last_merge_requests_sync=timezone.now() - timezone.timedelta(days=10))
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_user = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id, assignee=gl_user,
                                                      author=gl_user, state='closed'))
    _registry_merge_request(gl_mocker, gl_project, gl_merge_request)

    load_merge_requests()

    merge_request = MergeRequest.objects.first()

    check_merge_request(merge_request, gl_merge_request)

    project.refresh_from_db()
    assert timezone.datetime.date(project.gl_last_merge_requests_sync) == timezone.now().date()


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_merge_requests_server_error(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    with pytest.raises(GitlabGetError):
        load_merge_requests()


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_merge_requests_not_found(db, gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', status_code=status.HTTP_404_NOT_FOUND)

    load_merge_requests()


def _registry_merge_request(gl_mocker, gl_project, gl_merge_request):
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests', [gl_merge_request])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}', gl_merge_request)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/time_stats', GlTimeStats())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/closed_by', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/notes', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/participants', [])
