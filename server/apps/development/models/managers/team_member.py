# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import QuerySet


class TeamMemberManager(models.Manager):
    """The project group manager."""

    def get_no_watchers(self, team) -> QuerySet:
        """Get all users without watchers for team."""
        return self.filter(
            team=team,
            roles=~self.model.roles.WATCHER,
        ).values_list(
            'user',
            flat=True,
        )
