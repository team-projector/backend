# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import QuerySet


class TeamMemberManager(models.Manager):
    """The project group manager."""

    def get_no_watchers(self, team) -> QuerySet:
        """Get all users without watchers for team."""
        from apps.development.models import TeamMember

        return self.filter(
            team=team,
            roles=~TeamMember.roles.watcher,
        ).values_list(
            'user',
            flat=True,
        )
