from django.db.models import Q

from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles


def filter_available_salaries(queryset, user):
    teams = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [TeamMember.roles.leader]
    ).values_list('team_id', flat=True)

    users_query = Q(user__teams__in=teams) | Q(user=user.id)

    return queryset.filter(users_query)
