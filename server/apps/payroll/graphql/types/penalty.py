import graphene
from django.db.models import QuerySet

from apps.core.graphql.types import BaseModelObjectType
from apps.development.graphql.interfaces import WorkItem
from apps.payroll.graphql.types import SalaryType
from apps.payroll.models import Penalty
from apps.payroll.services.salary.allowed import filter_allowed_for_user
from apps.users.graphql.types import UserType


class PenaltyType(BaseModelObjectType):
    """Penalty type."""

    class Meta:
        model = Penalty

    owner = graphene.Field(WorkItem)
    user = graphene.Field(UserType)
    comment = graphene.String()
    sum = graphene.Float()  # noqa: WPS125
    created_by = graphene.Field(UserType)
    salary = graphene.Field(SalaryType)
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get salaries."""
        return filter_allowed_for_user(
            queryset,
            info.context.user if info.context.user.is_authenticated else None,
        )
