from django.db import models


class ProjectGroupMilestone(models.Model):
    """The ProjectGroupMilestone model."""

    class Meta:
        unique_together = ("milestone", "project_group")

    is_inherited = models.BooleanField(default=False)
    milestone = models.ForeignKey("development.Milestone", models.CASCADE)
    project_group = models.ForeignKey(
        "development.ProjectGroup",
        models.CASCADE,
    )

    def __str__(self):
        """Returns object string representation."""
        return self.pk
