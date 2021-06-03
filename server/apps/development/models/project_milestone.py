from django.db import models
from django.utils.translation import gettext_lazy as _


class ProjectMilestone(models.Model):
    """The ProjectMilestone model."""

    class Meta:
        unique_together = ("milestone", "project")
        verbose_name = _("VN__PROJECT_MILESTONE")
        verbose_name_plural = _("VN__PROJECT_MILESTONES")

    is_inherited = models.BooleanField(default=False)
    milestone = models.ForeignKey("development.Milestone", models.CASCADE)
    project = models.ForeignKey("development.Project", models.CASCADE)

    def __str__(self):
        """Returns object string representation."""
        return self.pk
