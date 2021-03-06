from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from jnt_django_toolbox.models.fields import EnumField

from apps.core.consts import DEFAULT_TITLE_LENGTH
from apps.core.models.mixins import GitlabEntityMixin
from apps.development.models.choices.project_state import ProjectState
from apps.development.models.milestone import MilestoneState


class Project(GitlabEntityMixin):
    """
    The project model.

    Fill from Gitlab.
    """

    class Meta:
        verbose_name = _("VN__PROJECT")
        verbose_name_plural = _("VN__PROJECTS")
        ordering = ("full_title", "title")

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

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("VN__IS_ACTIVE"),
        help_text=_("HT__IS_ACTIVE"),
    )

    gl_avatar = models.URLField(
        blank=True,
        verbose_name=_("VN__GITLAB_AVATAR"),
        help_text=_("HT__GITLAB_AVATAR"),
    )

    gl_last_issues_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("VN__GITLAB_LAST_ISSUES_SYNC"),
        help_text=_("HT__GITLAB_LAST_ISSUES_SYNC"),
    )

    gl_last_merge_requests_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("VN__GITLAB_MERGE_REQUESTS_SYNC"),
        help_text=_("HT__MERGE_REQUESTS_SYNC"),
    )

    state = EnumField(
        enum=ProjectState,
        default=ProjectState.DEVELOPING,
        verbose_name=_("VN__STATE"),
        help_text=_("HT__STATE"),
    )

    group = models.ForeignKey(
        "development.ProjectGroup",
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("VN__GROUP"),
        help_text=_("HT__GROUP"),
    )

    milestones = models.ManyToManyField(
        "development.Milestone",
        related_query_name="project",
        through="development.ProjectMilestone",
    )

    members = GenericRelation(  # noqa: CCE001
        "development.ProjectMember",
        related_query_name="project",
    )

    team = models.ForeignKey(
        "development.Team",
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name=_("VN__TEAM"),
        help_text=_("HT__TEAM"),
    )

    def __str__(self):
        """Returns object string representation."""
        return self.full_title or self.title

    def save(self, *args, **kwargs) -> None:
        """Save the current project."""
        if not self.full_title:
            self.full_title = self.title  # noqa: WPS601

        super().save(*args, **kwargs)

    @cached_property
    def active_milestones(self):
        """
        Return active milestones for current project.

        If milestones not found return milestones from parent group.
        """
        from apps.development.services.project_group.active_milestones import (  # noqa: WPS433, E501
            load_for_group,
        )

        milestones = self.milestones.filter(state=MilestoneState.ACTIVE)

        if not milestones and self.group:
            return load_for_group(self.group)

        return milestones
