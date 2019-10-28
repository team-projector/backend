# -*- coding: utf-8 -*-

from django.db import models


class SalaryManager(models.Manager):
    """The Salary model manager."""

    def allowed_for_user(self, user):
        """Get user salaries allowed for current user and team leader."""
        from apps.development.models import TeamMember  # noqa WPS433

        users = TeamMember.objects.filter(
            user=user,
            roles=TeamMember.roles.leader,
        ).values_list(
            'team__members',
            flat=True,
        )

        return self.filter(user__in=(*users, user.id))
