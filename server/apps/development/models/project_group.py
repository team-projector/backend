# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.consts import DEFAULT_TITLE_LENGTH
from apps.core.models.mixins import GitlabEntityMixin


class ProjectGroup(GitlabEntityMixin):
    """
    The project group model.

    Fill from Gitlab.
    """

    class Meta:
        verbose_name = _("VN__PROJECT_GROUP")
        verbose_name_plural = _("VN__PROJECT_GROUPS")
        ordering = ("title",)

    title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        verbose_name=_("VN__TITLE"),
        help_text=_("HT__TITLE"),
    )

    full_title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        blank=True,
        verbose_name=_("VN__FULL_TITLE"),
        help_text=_("HT__FULL_TITLE"),
    )

    gl_avatar = models.URLField(
        blank=True,
        verbose_name=_("VN__GITLAB_AVATAR"),
        help_text=_("HT__GITLAB_AVATAR"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("VN__IS_ACTIVE"),
        help_text=_("HT__IS_ACTIVE"),
    )

    parent = models.ForeignKey(
        "self",
        models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("VN__PARENT"),
        help_text=_("HT__PARENT"),
    )

    milestones = GenericRelation(
        "development.Milestone",
        related_query_name="project_group",
    )

    members = GenericRelation(  # noqa: CCE001
        "development.ProjectMember",
        related_query_name="project_group",
    )

    def __str__(self):
        """Returns object string representation."""
        return self.title
