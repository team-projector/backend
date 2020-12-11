from typing import List

from django.db import models
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import Milestone, ProjectGroup, ProjectMember
from apps.users.models import User

KEY_ID = "id"


def filter_allowed_for_user(
    queryset: models.QuerySet,
    user: User,
) -> models.QuerySet:
    """Get milestones for user."""
    members = get_members(user)

    project_milestones = Milestone.objects.filter(
        project__members__in=members,
    ).values(KEY_ID)

    milestones_ids = [
        milestone.get(KEY_ID) for milestone in project_milestones
    ]

    groups = ProjectGroup.objects.filter(members__in=members)

    milestones_ids = get_group_milestones(groups, milestones_ids)

    return queryset.filter(id__in=milestones_ids)


def get_members(user: User) -> List[ProjectMember]:
    """Get project managers."""
    members = ProjectMember.objects.filter(
        user=user,
    )

    if not members:
        raise GraphQLPermissionDenied(
            "Only project members can view milestones",
        )

    return list(members)


def get_group_milestones(
    groups: models.QuerySet,
    milestones_ids: List[int],
) -> List[int]:
    """Get milestones of groups."""
    milestones_on_level = Milestone.objects.filter(
        models.Q(project_group__in=groups)
        | models.Q(project__group__in=groups),
    ).values(KEY_ID)

    for milestone in milestones_on_level:
        milestones_ids.append(milestone.get(KEY_ID))

    children_groups = ProjectGroup.objects.filter(parent__in=groups)

    if children_groups:
        get_group_milestones(children_groups, milestones_ids)

    return milestones_ids


def is_project_manager(user: User, milestone: Milestone) -> bool:
    """Check project manager for current milestone."""
    members = ProjectMember.objects.filter(
        user=user,
        roles=ProjectMember.roles.MANAGER,
    )

    project_milestones = Milestone.objects.filter(
        project__members__in=members,
    ).values(KEY_ID)

    milestones_ids = [
        milestone.get(KEY_ID) for milestone in project_milestones
    ]

    groups = ProjectGroup.objects.filter(members__in=members)

    milestones_ids = get_group_milestones(groups, milestones_ids)

    return milestone.pk in milestones_ids
