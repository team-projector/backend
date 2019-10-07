# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from apps.core.consts import DEFAULT_TITLE_LENGTH
from apps.core.models.mixins import GitlabEntityMixin
from apps.development.models.milestone import MILESTONE_STATES
from apps.development.services.projects import get_group_active_milestones

from .managers import ProjectManager


class Project(GitlabEntityMixin):
    """
    The project model.

    Fill from Gitlab.
    """

    title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE'),
    )

    full_title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        null=True,
        blank=True,
        verbose_name=_('VN__FULL_TITLE'),
        help_text=_('HT__FULL_TITLE'),
    )

    group = models.ForeignKey(
        'development.ProjectGroup',
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('VN__GROUP'),
        help_text=_('HT__GROUP'),
    )

    gl_avatar = models.URLField(
        null=True,
        blank=True,
        verbose_name=_('VN__GITLAB_AVATAR'),
        help_text=_('HT__GITLAB_AVATAR'),
    )

    gl_last_issues_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('VN__GITLAB_LAST_ISSUES_SYNC'),
        help_text=_('HT__GITLAB_LAST_ISSUES_SYNC'),
    )

    gl_last_merge_requests_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('VN__GITLAB_MERGE_REQUESTS_SYNC'),
        help_text=_('HT__MERGE_REQUESTS_SYNC'),
    )

    milestones = GenericRelation(
        'Milestone',
        related_query_name='project',
    )
    members = GenericRelation(
        'development.ProjectMember',
        related_query_name='project',
    )

    objects = ProjectManager()

    class Meta:
        verbose_name = _('VN__PROJECT')
        verbose_name_plural = _('VN__PROJECTS')
        ordering = ('full_title', 'title')

    def __str__(self):
        return self.full_title or self.title

    def save(self, *args, **kwargs) -> None:
        """Save the current project."""
        if not self.full_title:
            self.full_title = self.title  # noqa WPS601

        super().save(*args, **kwargs)

    @cached_property
    def active_milestones(self):
        """
        Return active milestones for current project.

        If milestones not found return milestones from parent group.
        """
        ret = self.milestones.filter(state=MILESTONE_STATES.active)

        if not ret and self.group:
            return get_group_active_milestones(self.group)

        return ret or []
