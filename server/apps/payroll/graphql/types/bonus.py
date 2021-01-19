import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.types import BaseModelObjectType

from apps.development.graphql.interfaces import WorkItem
from apps.payroll.graphql.types import SalaryType
from apps.payroll.models import Bonus
from apps.payroll.services.salary.allowed import filter_allowed_for_user
from apps.users.graphql.types import UserType


class BonusType(BaseModelObjectType):
    """Bonus type."""

    class Meta:
        model = Bonus
        auth_required = True

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
        """Get bonuses."""
        return filter_allowed_for_user(queryset, info.context.user)
