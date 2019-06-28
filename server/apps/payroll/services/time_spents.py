from django.db.models import Q

from apps.development.models import TeamMember


def filter_available_spent_times(queryset, user):
    query = Q(user=user)
    query &= Q(
        Q(roles=TeamMember.roles.leader) | Q(roles=TeamMember.roles.watcher)
    )

    teams = TeamMember.objects.filter(query).values_list('team_id', flat=True)

    users_query = Q(user__teams__in=teams) | Q(user=user.id)

    return queryset.filter(users_query)
