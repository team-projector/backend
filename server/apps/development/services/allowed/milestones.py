from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet

from apps.development.models import ProjectGroup, ProjectMember, Milestone
from apps.users.models import User


def filter_allowed_for_user(queryset: QuerySet,
                            user: User) -> QuerySet:
    members = get_pm_members(user)

    milestones = Milestone.objects.filter(project__members__in=members)

    def fill_milestones(groups: QuerySet) -> None:
        nonlocal milestones

        milestones_on_level = Milestone.objects.filter(
            Q(project_group__in=groups) | Q(project__group__in=groups)
        )

        milestones = milestones | milestones_on_level  # WPS442

        children_groups = ProjectGroup.objects.filter(
            parent__in=groups
        )

        if children_groups:
            fill_milestones(children_groups)

    groups = ProjectGroup.objects.filter(members__in=members)

    fill_milestones(groups)

    return queryset.filter(id__in=milestones)


def get_pm_members(user: User):
    members = ProjectMember.objects.filter(
        user=user,
        role=ProjectMember.ROLE.project_manager
    )

    if not members:
        raise PermissionDenied(
            'Only project managers can view project resources'
        )

    return list(members)
