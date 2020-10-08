from django.db import models


class Timestamps(models.Model):
    """A mixin with created and updated fields."""

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Returns object string representation."""
        return str(self.created_at)
