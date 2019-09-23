from django.db import models


class SalaryManager(models.Manager):
    def allowed_for_user(self, user):
        from apps.development.models import TeamMember

        users = TeamMember.objects.filter(
            user=user,
            roles=TeamMember.roles.leader,
        ).values_list(
            'team__members',
            flat=True,
        )

        return self.filter(user__in=(*users, user.id))
