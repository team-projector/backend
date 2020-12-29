import graphene
from django.db.models import QuerySet

from apps.core.graphql.types import BaseModelObjectType
from apps.development.graphql.fields import TeamMembersConnectionField
from apps.development.graphql.types.team_metrics import TeamMetricsType
from apps.development.models import Team
from apps.development.services.team.allowed import filter_allowed_for_user
from apps.development.services.team.metrics.main import get_team_metrics


class TeamType(BaseModelObjectType):
    """Team type."""

    class Meta:
        model = Team

    title = graphene.String()
    metrics = graphene.Field(TeamMetricsType)
    members = TeamMembersConnectionField()

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get teams."""
        return filter_allowed_for_user(
            queryset,
            info.context.user if info.context.user.is_authenticated else None,
        )

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get team metrics."""
        return get_team_metrics(self)

    def resolve_members(self, info, **kwargs):  # noqa: WPS110
        """Get team members."""
        return self.teammember_set
