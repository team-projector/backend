from django.db import models


class ProjectMilestone(models.Model):
    """The ProjectMilestone model."""

    class Meta:
        unique_together = ("milestone", "project")

    is_inherited = models.BooleanField(default=False)
    milestone = models.ForeignKey("development.Milestone", models.CASCADE)
    project = models.ForeignKey("development.Project", models.CASCADE)

    def __str__(self):
        """Returns object string representation."""
        return self.pk
