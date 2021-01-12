import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.types import BaseModelObjectType

from apps.development.graphql.interfaces import MilestoneOwner
from apps.development.graphql.types.enums import MilestoneState
from apps.development.graphql.types.milestone_metrics import (
    MilestoneMetricsType,
)
from apps.development.models import Milestone
from apps.development.services.milestone.allowed import filter_allowed_for_user
from apps.development.services.milestone.metrics import (
    get_milestone_metrics_for_user,
)
from apps.development.services.milestone.problems import (
    get_milestone_problems_for_user,
)


class MilestoneType(BaseModelObjectType):
    """Milestone type."""

    class Meta:
        model = Milestone
        auth_required = True

    metrics = graphene.Field(MilestoneMetricsType)
    owner = graphene.Field(MilestoneOwner)
    problems = graphene.List(graphene.String)
    gl_url = graphene.String()
    gl_iid = graphene.Int()
    gl_last_sync = graphene.String()
    created_at = graphene.DateTime()
    title = graphene.String()
    description = graphene.String()
    start_date = graphene.Date()
    state = graphene.Field(MilestoneState)
    due_date = graphene.Date()
    budget = graphene.Float()

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get milestones."""
        return filter_allowed_for_user(queryset, info.context.user)

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get milestone metrics."""
        return get_milestone_metrics_for_user(info.context.user, self)

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get milestone problems."""
        return get_milestone_problems_for_user(info.context.user, self)
