import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.types import BitField

from apps.core.graphql import get_fields_from_info
from apps.core.graphql.fields import BaseModelConnectionField
from apps.core.graphql.types.model import BaseModelObjectType
from apps.skills.graphql.types import PositionType
from apps.users.graphql.fields import UserWorkBreaksConnectionField
from apps.users.graphql.types.user_metrics import UserMetricsType
from apps.users.models import User
from apps.users.services.user.metrics.main import UserMetricsProvider
from apps.users.services.user.problems import get_user_problems


class UserType(BaseModelObjectType):
    """User type."""

    class Meta:
        model = User

    name = graphene.String()
    login = graphene.String()
    last_login = graphene.DateTime()
    email = graphene.String()
    position = graphene.Field(PositionType)
    is_active = graphene.Boolean()
    hour_rate = graphene.Float()
    tax_rate = graphene.Float()
    annual_paid_work_breaks_days = graphene.Float()
    roles = BitField()
    gl_avatar = graphene.String()
    daily_work_hours = graphene.Int()
    teams = BaseModelConnectionField("development.TeamType")
    metrics = graphene.Field(UserMetricsType)
    problems = graphene.List(graphene.String)
    work_breaks = UserWorkBreaksConnectionField()

    @classmethod
    def get_queryset(
        cls,
        queryset: QuerySet,
        info,  # noqa: WPS110
    ) -> QuerySet:
        """Get queryset."""
        # TODO fix it (team members case)
        if issubclass(queryset.model, User):
            queryset = queryset.filter(is_active=True, roles__gt=0)

        return queryset

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get user metrics."""
        provider = UserMetricsProvider(get_fields_from_info(info))
        return provider.get_metrics(self)

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get user problems."""
        return get_user_problems(self)
