from typing import Any, Tuple

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


class IssueManager(models.Manager):
    def sync_gitlab(self, gl_id, **kwargs) -> Tuple[Any, bool]:
        kwargs['gl_last_sync'] = timezone.now()

        return self.update_or_create(
            gl_id=gl_id,
            defaults=kwargs
        )

    def allowed_for_user(self, user: User) -> QuerySet:
        from apps.development.models import TeamMember

        allowed_users = {user}

        members = filter_by_roles(
            TeamMember.objects.filter(user=user),
            [
                TeamMember.roles.leader,
                TeamMember.roles.watcher
            ]
        ).values_list(
            'team__members',
            flat=True
        )

        for member in members:
            allowed_users.add(member)

        return self.filter(user__in=allowed_users)
