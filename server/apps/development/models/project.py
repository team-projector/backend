from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import GitlabEntityMixin
from .project_group import ProjectGroup
from .project_member import ProjectMember
from ..db.managers import ProjectManager


class Project(GitlabEntityMixin):
    title = models.CharField(
        max_length=255,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE')
    )
    full_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('VN__FULL_TITLE'),
        help_text=_('HT__FULL_TITLE')
    )
    group = models.ForeignKey(
        ProjectGroup,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('VN__GROUP'),
        help_text=_('HT__GROUP')
    )

    gl_last_issues_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('VN__GITLAB_LAST_ISSUES_SYNC'),
        help_text=_('HT__GITLAB_LAST_ISSUES_SYNC')
    )

    milestones = GenericRelation(
        'Milestone',
        related_query_name='project'
    )
    members = GenericRelation(
        ProjectMember,
        related_query_name='project'
    )

    objects = ProjectManager()

    class Meta:
        verbose_name = _('VN__PROJECT')
        verbose_name_plural = _('VN__PROJECTS')
        ordering = ('full_title', 'title')

    def __str__(self):
        return self.full_title or self.title

    def save(self, *args, **kwargs) -> None:
        if not self.full_title:
            self.full_title = self.title

        super().save(*args, **kwargs)