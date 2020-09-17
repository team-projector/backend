# -*- coding: utf-8 -*-

from typing import List, Optional, Union

from gitlab.v4 import objects as gl

from apps.development.models import Issue, Label, MergeRequest
from apps.development.services.note.gl.sync import update_note_from_gitlab
from apps.development.services.project.gl.provider import ProjectGlProvider
from apps.development.services.project_group.gl.provider import (
    ProjectGroupGlProvider,
)
from apps.payroll.services.spent_time.updater import adjust_spent_times
from apps.users.services.user.gl.manager import UserGlManager


class BaseWorkItemGlManager:
    """Base gitlab manager for issues and merge requests."""

    def __init__(self):
        """Initializing."""
        self.project_provider = ProjectGlProvider()
        self.group_provider = ProjectGroupGlProvider()
        self.user_manager = UserGlManager()

    def sync_labels(
        self,
        target: Union[Issue, MergeRequest],
        gl_target: Union[gl.ProjectIssue, gl.MergeRequest],
        gl_project: gl.Project,
    ) -> None:
        """Load labels for work item."""
        project_labels = getattr(gl_project, "cached_labels", None)

        if project_labels is None:
            project_labels = gl_project.labels.list(all=True)
            gl_project.cached_labels = project_labels

        labels = []

        for label_title in gl_target.labels:
            label = self._get_or_create_label(label_title, project_labels)

            if label:
                labels.append(label)

        target.labels.set(labels)

    def sync_notes(
        self,
        target: Union[Issue, MergeRequest],
        gl_target: Union[gl.ProjectIssue, gl.MergeRequest],
    ) -> None:
        """Load notes for work item."""
        for gl_note in gl_target.notes.list(as_list=False):
            update_note_from_gitlab(gl_note, target)

        adjust_spent_times(target)

    def sync_participants(
        self,
        target: Union[Issue, MergeRequest],
        gl_target: Union[gl.ProjectIssue, gl.MergeRequest],
    ) -> None:
        """Load participants for work item."""
        target.participants.set(
            (
                self.user_manager.sync_user(user["id"])
                for user in gl_target.participants()
            ),
        )

    def _get_or_create_label(
        self,
        label_title: gl.ProjectLabel,
        project_labels: List[gl.ProjectLabel],
    ) -> Optional[Label]:
        """
        Get or create label.

        :param label_title:
        :type label_title: gl.ProjectLabel
        :param project_labels:
        :type project_labels: List[gl]
        :rtype: Optional[Label]
        """
        label = Label.objects.filter(title=label_title).first()

        return label or self._create_label(label_title, project_labels)

    def _create_label(
        self,
        label_title: gl.ProjectLabel,
        project_labels: List[gl.ProjectLabel],
    ) -> Optional[Label]:
        """
        Create label.

        :param label_title:
        :type label_title: gl.ProjectLabel
        :param project_labels:
        :type project_labels: List[gl]
        :rtype: Optional[Label]
        """
        gl_label = next(
            (
                project_label
                for project_label in project_labels
                if project_label.name == label_title
            ),
            None,
        )

        if gl_label:
            return Label.objects.create(
                title=label_title,
                color=gl_label.color,
            )

        return None
