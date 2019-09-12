from django.db.models import Q, QuerySet

from apps.development.models import ProjectGroup, ProjectMember, Milestone
from apps.users.models import User


def filter_allowed_for_user(queryset: QuerySet,
                            user: User) -> QuerySet:
    milestones = Milestone.objects.filter(
        project__members__user=user,
        project__members__role=ProjectMember.ROLE.project_manager
    )

    def fill_milestones(groups: QuerySet) -> None:
        nonlocal milestones

        milestones_on_level = Milestone.objects.filter(
            Q(project_group__in=groups) | Q(project__group__in=groups)
        )

        milestones = milestones | milestones_on_level  # noqa:WPS442

        children_groups = ProjectGroup.objects.filter(
            parent__in=groups
        )

        if children_groups:
            fill_milestones(children_groups)

    groups = ProjectGroup.objects.filter(
        members__user=user,
        members__role=ProjectMember.ROLE.project_manager
    )

    fill_milestones(groups)

    queryset = queryset.intersection(milestones)

    return queryset
