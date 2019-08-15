from typing import Any

from graphql import ResolveInfo
from rest_framework.generics import get_object_or_404

from apps.development.models import TeamMember
from apps.payroll.models import WorkBreak
from apps.payroll.services.users import user_related_with_another_by_team_roles


class CanManageWorkBreak:
    @staticmethod
    def has_mutation_permission(root: Any,
                                info: ResolveInfo,
                                **kwargs) -> bool:
        work_break = get_object_or_404(
            WorkBreak.objects.all(),
            pk=kwargs['id']
        )

        return user_related_with_another_by_team_roles(
            info.context.user,
            work_break.user,
            [TeamMember.roles.leader]
        ) or work_break.user == info.context.user
