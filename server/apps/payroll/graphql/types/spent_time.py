import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.types import BaseModelObjectType

from apps.development.graphql.interfaces import WorkItem
from apps.payroll.graphql.types import SalaryType
from apps.payroll.models import SpentTime
from apps.payroll.services.spent_time.allowed import filter_allowed_for_user
from apps.users.graphql.types import UserType


class SpentTimeType(BaseModelObjectType):
    """Spent Time type."""

    class Meta:
        model = SpentTime
        auth_required = True

    owner = graphene.Field(WorkItem)
    user = graphene.Field(UserType)
    sum = graphene.Float()  # noqa: WPS125
    created_by = graphene.Field(UserType)
    salary = graphene.Field(SalaryType)
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()
    date = graphene.Date()
    customer_sum = graphene.Float()
    hour_rate = graphene.Float()
    tax_rate = graphene.Float()
    customer_rate = graphene.Float()
    time_spent = graphene.Float()

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get spent times."""
        return filter_allowed_for_user(queryset, info.context.user)

    def resolve_owner(self, info, **kwargs):  # noqa: WPS110
        """Get spent time owner: issue or merge request."""
        return self.base
