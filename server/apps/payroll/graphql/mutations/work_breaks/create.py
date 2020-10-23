import graphene
from jnt_django_graphene_toolbox.mutations import BaseMutation
from jnt_django_graphene_toolbox.mutations.mixins import (
    ArgumentsValidationMixin,
)

from apps.payroll.graphql.forms import WorkBreakForm
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak


class CreateWorkBreakMutation(ArgumentsValidationMixin, BaseMutation):
    """Create work break mutation."""

    class Arguments:
        comment = graphene.String(required=True)
        from_date = graphene.DateTime(required=True)
        reason = graphene.String(required=True)
        to_date = graphene.DateTime(required=True)
        user = graphene.ID(required=True)

    form_class = WorkBreakForm

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def perform_mutate(cls, info, cleaned_data):  # noqa: WPS110
        """Create work break after validation."""
        work_break = WorkBreak.objects.create(**cleaned_data)

        return cls(work_break=work_break)
