from django.contrib.auth import get_user_model

from apps.development.models import TeamMember

User = get_user_model()


def filter_available_work_breaks(queryset, user):
    users = TeamMember.objects.filter(
        user=user,
        roles=TeamMember.roles.leader
    ).values_list(
        'team__members',
        flat=True
    )

    return queryset.filter(user__in=(*users, user.id))
