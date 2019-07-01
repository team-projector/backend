from django.test import override_settings

from apps.core.gitlab import get_gitlab_client
from apps.development.models import MergeRequest, Note
from apps.development.services.gitlab.merge_requests import (
    load_merge_request_notes, load_merge_request_labels, load_project_merge_request, load_merge_requests
)
from tests.test_development.factories import ProjectFactory, MergeRequestFactory, ProjectMilestoneFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlUserFactory, GlProjectFactory, GlMergeRequestFactory, GlNoteFactory, GlLabelFactory, GlTimeStats,
    GlProjectMilestoneFactory
)
from tests.test_development.mocks import activate_httpretty, registry_get_gl_url


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate_httpretty
def test_load_merge_request_notes(db):
    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id))
    merge_request = MergeRequestFactory.create(gl_id=gl_merge_request.id, gl_iid=gl_merge_request.iid, project=project)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}',
                        gl_merge_request)

    gl_author = AttrDict(GlUserFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/users/{gl_author.id}', gl_author)

    gl_note = AttrDict(GlNoteFactory(author=gl_author, body='added 1h of time spent at 2000-01-01'))
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}'
                        f'/notes', [gl_note])

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
    _check_user(note.user, gl_author)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate_httpretty
def test_load_merge_request_labels(db):
    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)

    gl_label = AttrDict(GlLabelFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/labels', [gl_label])

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id), labels=[gl_label])
    merge_request = MergeRequestFactory.create(gl_id=gl_merge_request.id, gl_iid=gl_merge_request.iid, project=project)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}',
                        gl_merge_request)

    gl_project_loaded = gl.projects.get(id=project.gl_id)
    gl_merge_request_loaded = gl_project_loaded.mergerequests.get(id=merge_request.gl_iid)

    load_merge_request_labels(merge_request, gl_project_loaded, gl_merge_request_loaded)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate_httpretty
def test_load_project_merge_request(db):
    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
    gl = get_gitlab_client()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)

    gl_user = AttrDict(GlUserFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/users/{gl_user.id}', gl_user)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    milestone = ProjectMilestoneFactory.create(gl_id=gl_milestone.id)

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id, assignee=gl_user, author=gl_user,
                                                      state='closed', milestone=gl_milestone))
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}',
                        gl_merge_request)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}'
                        f'/time_stats', GlTimeStats())
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}'
                        f'/closed_by', [])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/labels', [])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}'
                        f'/notes', [])

    gl_project_loaded = gl.projects.get(id=project.gl_id)
    gl_merge_request_loaded = gl_project_loaded.mergerequests.get(id=gl_merge_request.iid)

    load_project_merge_request(project, gl_project_loaded, gl_merge_request_loaded)

    merge_request = MergeRequest.objects.first()

    _check_merge_request(merge_request, gl_merge_request_loaded)
    _check_user(merge_request.author, gl_user)
    _check_user(merge_request.assignee, gl_user)
    assert merge_request.milestone == milestone


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@activate_httpretty
def test_load_merge_requests(db):
    registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)

    gl_user = AttrDict(GlUserFactory())
    registry_get_gl_url(f'https://gitlab.com/api/v4/users/{gl_user.id}', gl_user)

    gl_merge_request = AttrDict(GlMergeRequestFactory(project_id=gl_project.id, assignee=gl_user,
                                                      author=gl_user, state='closed'))
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests', [gl_merge_request])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}',
                        gl_merge_request)
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}'
                        f'/time_stats', GlTimeStats())
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}'
                        f'/closed_by', [])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/labels', [])
    registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}'
                        f'/notes', [])

    load_merge_requests()

    merge_request = MergeRequest.objects.first()

    _check_merge_request(merge_request, gl_merge_request)


def _check_merge_request(merge_request, gl_merge_request):
    assert merge_request.gl_id == gl_merge_request.id
    assert merge_request.gl_iid == gl_merge_request.iid
    assert merge_request.gl_url == gl_merge_request.web_url
    assert merge_request.title == gl_merge_request.title
    assert merge_request.state == gl_merge_request.state
    assert merge_request.created_at is not None
    assert merge_request.updated_at is not None


def _check_user(user, gl_user):
    assert user.login == gl_user.username
    assert user.name == gl_user.name
    assert user.gl_avatar == gl_user.avatar_url
    assert user.gl_url == gl_user.web_url
