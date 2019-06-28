from django.db.models import Q

from apps.development.models import TeamMember
from apps.payroll.models import SpentTime


def get_available_spent_times(user, queryset=None):
    query = Q(user=user)
    query &= Q(
        Q(roles=TeamMember.roles.leader) | Q(roles=TeamMember.roles.watcher)
    )

    teams = TeamMember.objects.filter(query).values_list('team_id', flat=True)

    users_query = Q(user__teams__in=teams) | Q(user=user.id)

    if queryset is None:
        queryset = SpentTime.objects.all()

    return queryset.filter(users_query)
