# -*- coding: utf-8 -*-

from django.db import models


class TeamMemberManager(models.Manager):
    """The project group manager."""

    def get_no_watchers(self, team) -> models.QuerySet:
        """Get all users without watchers for team."""
        return self.filter(
            team=team,
            roles=~self.model.roles.WATCHER,
        ).values_list(
            "user",
            flat=True,
        )
