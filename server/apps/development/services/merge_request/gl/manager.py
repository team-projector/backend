# -*- coding: utf-8 -*-

import logging

from django.utils import timezone
from gitlab.v4 import objects as gl

from apps.core.gitlab.parsers import parse_gl_datetime
from apps.development import models
from apps.development.models import MergeRequest
from apps.development.services.gl.work_item_manager import (
    BaseWorkItemGlManager,
)

logger = logging.getLogger(__name__)


class MergeRequestGlManager(BaseWorkItemGlManager):
    """Merge requests gitlab manager."""

    def sync_merge_requests(self, full_reload: bool = False) -> None:
        """Sync merge requests from all projects."""
        for project in models.Project.objects.all():
            self.sync_project_merge_requests(project, full_reload)

    def sync_project_merge_requests(
        self, project: models.Project, full_reload: bool = False,
    ) -> None:
        """Load merge requests from project."""
        gl_project = self.project_provider.get_gl_project(project)
        if not gl_project:
            return

        logger.info("Syncing project '%s' merge_requests", project)

        args = {
            "as_list": False,
        }

        if not full_reload and project.gl_last_merge_requests_sync:
            args["updated_after"] = project.gl_last_merge_requests_sync

        for gl_merge_request in gl_project.mergerequests.list(**args):
            self.update_merge_request(
                project, gl_project, gl_merge_request,
            )

        project.gl_last_merge_requests_sync = timezone.now()
        project.save(update_fields=("gl_last_merge_requests_sync",))

    def update_merge_request(
        self,
        project: models.Project,
        gl_project: gl.Project,
        gl_merge_request: gl.MergeRequest,
    ) -> MergeRequest:
        """Load full info for merge request for project."""
        time_stats = gl_merge_request.time_stats()

        fields = {
            "gl_id": gl_merge_request.id,
            "gl_iid": gl_merge_request.iid,
            "gl_url": gl_merge_request.web_url,
            "project": project,
            "title": gl_merge_request.title,
            "total_time_spent": time_stats["total_time_spent"],
            "time_estimate": time_stats["time_estimate"],
            "state": gl_merge_request.state.upper(),
            "created_at": parse_gl_datetime(gl_merge_request.created_at),
            "updated_at": parse_gl_datetime(gl_merge_request.updated_at),
            "closed_at": parse_gl_datetime(gl_merge_request.closed_at),
            "user": self.user_manager.extract_user_from_data(
                gl_merge_request.assignee,
            ),
            "author": self.user_manager.extract_user_from_data(
                gl_merge_request.author,
            ),
        }

        if gl_merge_request.milestone:
            milestone = models.Milestone.objects.filter(
                gl_id=gl_merge_request.milestone["id"],
            ).first()

            if milestone:
                fields["milestone"] = milestone

        merge_request, _ = models.MergeRequest.objects.update_from_gitlab(
            **fields,
        )

        self.sync_labels(merge_request, gl_merge_request, gl_project)
        self.sync_notes(merge_request, gl_merge_request)
        self.sync_participants(merge_request, gl_merge_request)

        logger.info("Merge Request '%s' is synced", merge_request)

        return merge_request
