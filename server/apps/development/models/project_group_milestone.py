from django.db import models
from django.utils.translation import gettext_lazy as _


class ProjectGroupMilestone(models.Model):
    """The ProjectGroupMilestone model."""

    class Meta:
        unique_together = ("milestone", "project_group")
        verbose_name = _("VN__PROJECT_GROUP_MILESTONE")
        verbose_name_plural = _("VN__PROJECT_GROUP_MILESTONES")

    is_inherited = models.BooleanField(default=False)
    milestone = models.ForeignKey("development.Milestone", models.CASCADE)
    project_group = models.ForeignKey(
        "development.ProjectGroup",
        models.CASCADE,
    )

    def __str__(self):
        """Returns object string representation."""
        return self.pk
