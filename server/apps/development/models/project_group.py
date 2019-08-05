from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import GitlabEntityMixin
from .project_member import ProjectMember
from ..db.managers import ProjectGroupManager


class ProjectGroup(GitlabEntityMixin):
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

    gl_avatar_url = models.URLField(
        null=True,
        blank=True,
        verbose_name=_('VN__GITLAB_AVATAR_URL'),
        help_text=_('HT__GITLAB_AVATAR_URL')
    )

    parent = models.ForeignKey(
        'self',
        models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('VN__PARENT'),
        help_text=_('HT__PARENT')
    )

    milestones = GenericRelation(
        'Milestone',
        related_query_name='project_group'
    )
    members = GenericRelation(
        ProjectMember,
        related_query_name='project_group'
    )

    objects = ProjectGroupManager()

    class Meta:
        verbose_name = _('VN__PROJECT_GROUP')
        verbose_name_plural = _('VN__PROJECT_GROUPS')
        ordering = ('title',)

    def __str__(self):
        return self.title
