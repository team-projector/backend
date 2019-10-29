# -*- coding: utf-8 -*-

import logging

from django.utils import timezone
from gitlab.v4 import objects as gl

from apps.core.gitlab.parsers import parse_gl_datetime
from apps.development import models
from apps.development.models import MergeRequest
from apps.development.services.project.gl.provider import ProjectGlProvider
from apps.development.services.project_group.gl.provider import (
    ProjectGroupGlProvider,
)
from apps.users.services.user.gl.manager import UserGlManager

logger = logging.getLogger(__name__)


class MergeRequestGlManager:
    """Merge requests gitlab manager."""

    def __init__(self):
        """Initializing."""
        self.project_provider = ProjectGlProvider()
        self.group_provider = ProjectGroupGlProvider()
        self.user_manager = UserGlManager()

    def sync_merge_requests(
        self,
        full_reload: bool = False,
    ) -> None:
        """Sync merge requests from all projects."""
        for project in models.Project.objects.all():
            self.sync_project_merge_requests(project, full_reload)

    def sync_project_merge_requests(
        self,
        project: models.Project,
        full_reload: bool = False,
    ) -> None:
        """Load merge requests from project."""
        gl_project = self.project_provider.get_gl_project(project)
        if not gl_project:
            return

        logger.info(f'Syncing project "{project}" merge_requests')

        args = {
            'as_list': False,
        }

        if not full_reload and project.gl_last_merge_requests_sync:
            args['updated_after'] = project.gl_last_merge_requests_sync

        for gl_merge_request in gl_project.mergerequests.list(**args):
            self.update_merge_request(
                project,
                gl_project,
                gl_merge_request,
            )

        project.gl_last_merge_requests_sync = timezone.now()
        project.save(update_fields=('gl_last_merge_requests_sync',))

    def update_merge_request(
        self,
        project: models.Project,
        gl_project: gl.Project,
        gl_merge_request: gl.MergeRequest,
    ) -> MergeRequest:
        """Load full info for merge request for project."""
        time_stats = gl_merge_request.time_stats()

        fields = {
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
            'user': self.user_manager.extract_user_from_data(
                gl_merge_request.assignee,
            ),
            'author': self.user_manager.extract_user_from_data(
                gl_merge_request.author,
            ),
        }

        if gl_merge_request.milestone:
            milestone = models.Milestone.objects.filter(
                gl_id=gl_merge_request.milestone['id'],
            ).first()

            if milestone:
                fields['milestone'] = milestone

        merge_request, _ = models.MergeRequest.objects.update_from_gitlab(
            **fields,
        )

        self.sync_labels(merge_request, gl_merge_request, gl_project)
        self.sync_notes(merge_request, gl_merge_request)
        self.sync_participants(merge_request, gl_merge_request)

        logger.info(f'Merge Request "{merge_request}" is synced')

        return merge_request

    def sync_labels(
        self,
        merge_request: models.MergeRequest,
        gl_merge_request: gl.MergeRequest,
        gl_project: gl.Project,
    ) -> None:
        """Load labels for merge request."""
        project_labels = getattr(gl_project, 'cached_labels', None)
        if project_labels is None:
            project_labels = gl_project.labels.list(all=True)
            gl_project.cached_labels = project_labels

        labels = []

        for label_title in gl_merge_request.labels:
            label = models.Label.objects.filter(title=label_title).first()
            if not label:
                gl_label = next((
                    project_label
                    for project_label in project_labels
                    if project_label.name == label_title
                ),
                    None,
                )
                if gl_label:
                    label = models.Label.objects.create(
                        title=label_title,
                        color=gl_label.color,
                    )

            if label:
                labels.append(label)

        merge_request.labels.set(labels)

    def sync_notes(
        self,
        merge_request: models.MergeRequest,
        gl_merge_request: gl.MergeRequest,
    ) -> None:
        """Load notes for merge request."""
        for gl_note in gl_merge_request.notes.list(as_list=False, system=True):
            models.Note.objects.update_from_gitlab(
                gl_note,
                merge_request,
            )

        merge_request.adjust_spent_times()

    def sync_participants(
        self,
        merge_request: models.MergeRequest,
        gl_merge_request: gl.MergeRequest,
    ) -> None:
        """Load participants for merge request."""
        merge_request.participants.set((
            self.user_manager.sync_user(user['id'])
            for user in gl_merge_request.participants()
        ))
