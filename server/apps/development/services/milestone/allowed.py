# -*- coding: utf-8 -*-

from typing import List

from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet

from apps.development.models import Milestone, ProjectGroup, ProjectMember
from apps.development.models.project_member import PROJECT_MEMBER_ROLES
from apps.users.models import User


def filter_allowed_for_user(
    queryset: QuerySet,
    user: User,
) -> QuerySet:
    """Get milestones for user."""
    members = get_members(user)

    project_milestones = Milestone.objects.filter(
        project__members__in=members,
    ).values('id')

    milestones_ids = [milestone.get('id') for milestone in project_milestones]

    groups = ProjectGroup.objects.filter(members__in=members)

    milestones_ids = get_group_milestones(groups, milestones_ids)

    return queryset.filter(id__in=milestones_ids)


def get_members(user: User) -> List[ProjectMember]:
    """Get project managers."""
    members = ProjectMember.objects.filter(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
    )

    if not members:
        raise PermissionDenied(
            'Only project managers can view project resources',
        )

    return list(members)


def get_group_milestones(
    groups: QuerySet,
    milestones_ids: List[int],
) -> List[int]:
    """Get milestones of groups."""
    milestones_on_level = Milestone.objects.filter(
        Q(project_group__in=groups) | Q(project__group__in=groups),
    ).values('id')

    for milestone in milestones_on_level:
        milestones_ids.append(milestone.get('id'))

    children_groups = ProjectGroup.objects.filter(
        parent__in=groups,
    )

    if children_groups:
        get_group_milestones(children_groups, milestones_ids)

    return milestones_ids
