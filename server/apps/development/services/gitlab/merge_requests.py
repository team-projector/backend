import logging

from django.utils import timezone
from gitlab import GitlabGetError
from gitlab.v4.objects import (
    Project as GlProject, MergeRequest as GlMergeRequest
)
from rest_framework import status

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from apps.users.models import User
from .parsers import parse_gl_datetime
from .users import extract_user_from_data, load_user
from ...models import Label, MergeRequest, Milestone, Note, Project

logger = logging.getLogger(__name__)


def load_merge_requests(full_reload: bool = False) -> None:
    for project in Project.objects.all():
        try:
            load_project_merge_requests(project, full_reload)
        except GitlabGetError as e:
            if e.response_code != status.HTTP_404_NOT_FOUND:
                raise


def load_project_merge_requests(project: Project,
                                full_reload: bool = False) -> None:
    gl = get_gitlab_client()

    logger.info(f'Syncing project "{project}" merge_requests')
    gl_project = gl.projects.get(id=project.gl_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    args = {
        'as_list': False
    }

    if not full_reload and project.gl_last_merge_requests_sync:
        args['updated_after'] = project.gl_last_merge_requests_sync

    project.gl_last_merge_requests_sync = timezone.now()
    project.save(update_fields=['gl_last_merge_requests_sync'])

    for gl_merge_request in gl_project.mergerequests.list(**args):
        load_project_merge_request(project, gl_project, gl_merge_request)


def load_project_merge_request(project: Project,
                               gl_project: GlProject,
                               gl_mr: GlMergeRequest) -> MergeRequest:
    time_stats = gl_mr.time_stats()

    params = {
        'gl_id': gl_mr.id,
        'gl_iid': gl_mr.iid,
        'gl_url': gl_mr.web_url,
        'project': project,
        'title': gl_mr.title,
        'total_time_spent': time_stats['total_time_spent'],
        'time_estimate': time_stats['time_estimate'],
        'state': gl_mr.state,
        'created_at': parse_gl_datetime(gl_mr.created_at),
        'updated_at': parse_gl_datetime(gl_mr.updated_at),
        'closed_at': parse_gl_datetime(gl_mr.closed_at),
        'user': extract_user_from_data(gl_mr.assignee),
        'author': extract_user_from_data(gl_mr.author),
    }

    if gl_mr.milestone:
        milestone = Milestone.objects.filter(
            gl_id=gl_mr.milestone['id']
        ).first()

        if milestone:
            params['milestone'] = milestone

    merge_request, _ = MergeRequest.objects.sync_gitlab(**params)

    load_merge_request_labels(merge_request, gl_project, gl_mr)
    load_merge_request_notes(merge_request, gl_mr)
    load_merge_request_participants(merge_request, gl_mr)

    logger.info(f'MergeRequest "{merge_request}" is synced')

    return merge_request


def load_merge_request_labels(merge_request: MergeRequest,
                              gl_project: GlProject,
                              gl_merge_request: GlMergeRequest) -> None:
    project_labels = getattr(gl_project, '_cache_labels', None)
    if project_labels is None:
        project_labels = gl_project.labels.list(all=True)
        gl_project._cache_labels = project_labels

    labels = []

    for label_title in gl_merge_request.labels:
        label = Label.objects.filter(title=label_title).first()
        if not label:
            gl_label = next((
                x
                for x in project_labels
                if x.name == label_title
            ), None)
            if gl_label:
                label = Label.objects.create(
                    title=label_title,
                    color=gl_label.color
                )

        if label:
            labels.append(label)

    merge_request.labels.set(labels)


def load_merge_request_notes(merge_request: MergeRequest,
                             gl_merge_request: GlMergeRequest) -> None:
    for gl_note in gl_merge_request.notes.list(as_list=False, system=True):
        Note.objects.sync_gitlab(gl_note, merge_request)

    merge_request.adjust_spent_times()


def load_merge_request_participants(merge_request: MergeRequest,
                                    gl_merge_request: GlMergeRequest) -> None:
    def get_user(gl_id: int) -> User:
        return User.objects.filter(gl_id=gl_id).first() or load_user(gl_id)

    merge_request.participants.set((
        get_user(x['id'])
        for x in gl_merge_request.participants()
    ))
