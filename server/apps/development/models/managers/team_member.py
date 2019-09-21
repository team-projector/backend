from django.db import models
from django.db.models import QuerySet


class TeamMemberManager(models.Manager):
    def get_no_watchers(self, team) -> QuerySet:
        from apps.development.models import TeamMember

        return self.filter(
            team=team,
            roles=~TeamMember.roles.watcher,
        ).values_list(
            'user',
            flat=True,
        )
