from django.db import models


class TeamMemberManager(models.Manager):
    """The project group manager."""

    def get_no_watchers(self, team) -> models.QuerySet:
        """Get all users without watchers for team."""
        query = models.Q(team=team)
        query &= models.Q(roles=self.model.roles.LEADER) | models.Q(
            roles=self.model.roles.DEVELOPER,
        )
        return self.filter(query).values_list("user", flat=True)
