from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet

from apps.development.models import Milestone, ProjectGroup, ProjectMember
from apps.users.models import User


def filter_allowed_for_user(queryset: QuerySet,
                            user: User) -> QuerySet:
    members = get_members(user)

    project_milestones = Milestone.objects.filter(
        project__members__in=members,
    ).values('id')

    milestones_ids = [item.get('id') for item in project_milestones]

    groups = ProjectGroup.objects.filter(members__in=members)

    milestones_ids = get_group_milestones(groups, milestones_ids)

    return queryset.filter(id__in=milestones_ids)


def get_members(user: User) -> list:
    members = ProjectMember.objects.filter(
        user=user,
        role=ProjectMember.ROLE.project_manager,
    )

    if not members:
        raise PermissionDenied(
            'Only project managers can view project resources',
        )

    return list(members)


def get_group_milestones(groups: QuerySet,
                         milestones_ids: list) -> list:
    milestones_on_level = Milestone.objects.filter(
        Q(project_group__in=groups) | Q(project__group__in=groups),
    ).values('id')

    for item in milestones_on_level:
        milestones_ids.append(item.get('id'))

    children_groups = ProjectGroup.objects.filter(
        parent__in=groups,
    )

    if children_groups:
        get_group_milestones(children_groups, milestones_ids)

    return milestones_ids
