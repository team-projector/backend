# -*- coding: utf-8 -*-

from typing import Any

from graphql import ResolveInfo
from rest_framework.generics import get_object_or_404

from apps.development.models import TeamMember
from apps.payroll.models import WorkBreak
from apps.users.services import user as user_service


class CanApproveDeclineWorkBreak:
    """Permissions can approve or decline work break."""

    def has_mutation_permission(
        self,
        root: Any,
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ) -> bool:
        """Only team leader can approve or decline work break."""
        work_break = get_object_or_404(
            WorkBreak.objects.all(),
            pk=kwargs['id'],
        )

        return user_service.is_related_with_another_by_team_roles(
            info.context.user,
            work_break.user,
            [TeamMember.roles.LEADER],
        )
