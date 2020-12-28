import graphene
from django.db.models import QuerySet

from apps.core.graphql.types import BaseModelObjectType
from apps.payroll.models import WorkBreak
from apps.payroll.models.mixins.approved import ApprovedState
from apps.payroll.models.work_break import WorkBreakReason
from apps.payroll.services.work_break.allowed import filter_allowed_for_user
from apps.users.graphql.types import UserType


class WorkBreakType(BaseModelObjectType):
    """Work break type."""

    class Meta:
        model = WorkBreak

    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()
    approved_at = graphene.DateTime()
    from_date = graphene.Date()
    to_date = graphene.Date()
    approved_by = graphene.Field(UserType)
    approve_state = graphene.Field(graphene.Enum.from_enum(ApprovedState))
    decline_reason = graphene.String()
    comment = graphene.String()
    paid = graphene.Boolean()
    user = graphene.Field(UserType)
    paid_days = graphene.Field(UserType)
    reason = graphene.Field(graphene.Enum.from_enum(WorkBreakReason))

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get work breaks."""
        return filter_allowed_for_user(queryset, info.context.user)
