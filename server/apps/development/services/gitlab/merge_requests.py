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
from .parsers import parse_gl_datetime
from .users import extract_user_from_data
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
                               gl_merge_request: GlMergeRequest) -> None:
    time_stats = gl_merge_request.time_stats()

    params = {
        'gl_id': gl_merge_request.id,
        'gl_iid': gl_merge_request.iid,
        'gl_url': gl_merge_request.web_url,
        'project': project,
        'title': gl_merge_request.title,
        'total_time_spent': time_stats['total_time_spent'],
        'time_estimate': time_stats['time_estimate'],
        'state': gl_merge_request.state,
        'created_at': parse_gl_datetime(gl_merge_request.created_at),
        'updated_at': parse_gl_datetime(gl_merge_request.updated_at),
        'closed_at': parse_gl_datetime(gl_merge_request.closed_at),
        'assignee': extract_user_from_data(gl_merge_request.assignee),
        'author': extract_user_from_data(gl_merge_request.author),
    }

    if gl_merge_request.milestone:
        milestone = Milestone.objects.filter(
            gl_id=gl_merge_request.milestone['id']
        ).first()

        if milestone:
            params['milestone'] = milestone

    merge_request, _ = MergeRequest.objects.sync_gitlab(**params)

    load_merge_request_labels(merge_request, gl_project, gl_merge_request)
    load_merge_request_notes(merge_request, gl_merge_request)

    logger.info(f'MergeRequest "{merge_request}" is synced')


def load_merge_request_labels(merge_request: MergeRequest,
                              gl_project: GlProject,
                              gl_merge_request: GlMergeRequest) -> None:
    project_labels = getattr(gl_project, '_cache_labels', None)
    if project_labels is None:
        project_labels = gl_project.labels.list(all=True)
        setattr(gl_project, '_cache_labels', project_labels)

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
