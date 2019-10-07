# -*- coding: utf-8 -*-

from django.db import models


class WorkBreakManager(models.Manager):
    """The Work Break model manager."""

    def allowed_for_user(self, user):
        """Get user work breaks allowed for current user and team leader."""
        from apps.development.models import TeamMember

        users = TeamMember.objects.filter(
            user=user,
            roles=TeamMember.roles.leader,
        ).values_list(
            'team__members',
            flat=True,
        )

        return self.filter(user__in=(*users, user.id))
