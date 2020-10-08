from typing import Optional

from graphql import ResolveInfo

from apps.core.graphql.helpers.generics import get_object_or_not_found
from apps.development.models import TeamMember
from apps.payroll.models import WorkBreak
from apps.users.services.user.relations import (
    is_related_with_another_by_team_roles,
)


class CanApproveDeclineWorkBreak:
    """Permissions can approve or decline work break."""

    def has_mutation_permission(
        self,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ) -> bool:
        """Only team leader can approve or decline work break."""
        work_break = get_object_or_not_found(
            WorkBreak.objects.all(),
            pk=kwargs["id"],
        )

        return is_related_with_another_by_team_roles(
            info.context.user,  # type:ignore
            work_break.user,
            [TeamMember.roles.LEADER],
        )
