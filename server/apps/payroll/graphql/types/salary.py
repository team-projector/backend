import graphene
from django.db.models import QuerySet

from apps.core.graphql.types import BaseModelObjectType
from apps.development.graphql.interfaces import WorkItem
from apps.payroll.models import Salary
from apps.payroll.services.salary.allowed import filter_allowed_for_user
from apps.skills.graphql.types import PositionType
from apps.users.graphql.types import UserType


class SalaryType(BaseModelObjectType):
    """Salary type."""

    class Meta:
        model = Salary
        auth_required = True

    owner = graphene.Field(WorkItem)
    user = graphene.Field(UserType)
    created_at = graphene.DateTime()
    period_from = graphene.DateTime()
    period_to = graphene.DateTime()
    charged_time = graphene.Int()
    hour_rate = graphene.Float()
    tax_rate = graphene.Float()
    taxes = graphene.Float()
    bonus = graphene.Float()
    penalty = graphene.Float()
    sum = graphene.Float()  # noqa: WPS125
    total = graphene.Float()
    payed = graphene.Boolean()
    comment = graphene.String()
    created_by = graphene.Field(UserType)
    position = graphene.Field(PositionType)

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get salaries."""
        return filter_allowed_for_user(queryset, info.context.user)
