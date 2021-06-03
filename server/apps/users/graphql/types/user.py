import graphene
from django.db import models
from jnt_django_graphene_toolbox.fields import (
    BaseModelConnectionField,
    BitField,
)
from jnt_django_graphene_toolbox.helpers.selected_fields import (
    get_fields_from_info,
)
from jnt_django_graphene_toolbox.types import BaseModelObjectType

from apps.core import injector
from apps.skills.graphql.types import PositionType
from apps.users.graphql import fields, resolvers, types
from apps.users.logic.services import IUserMetricsService, IUserProblemsService
from apps.users.models import User
from apps.users.models.user import UserRole


class UserType(BaseModelObjectType):
    """User type."""

    class Meta:
        model = User
        auth_required = True

    name = graphene.String()
    login = graphene.String()
    last_login = graphene.DateTime()
    email = graphene.String()
    gl_token = graphene.String()
    position = graphene.Field(PositionType)
    is_active = graphene.Boolean()
    hour_rate = graphene.Float()
    customer_hour_rate = graphene.Float()
    tax_rate = graphene.Float()
    annual_paid_work_breaks_days = graphene.Float()
    roles = BitField(UserRole)
    gl_avatar = graphene.String()
    daily_work_hours = graphene.Int()
    teams = BaseModelConnectionField("apps.development.graphql.types.TeamType")
    metrics = graphene.Field(types.UserMetricsType)
    problems = graphene.List(graphene.String)
    work_breaks = fields.UserWorkBreaksConnectionField()
    issues_summary = graphene.Field(
        types.UserIssuesSummaryType,
        resolver=resolvers.resolve_user_issues_summary,
        project=graphene.ID(),
        due_date=graphene.Date(),
    )

    @classmethod
    def get_queryset(
        cls,
        queryset: models.QuerySet,
        info,  # noqa: WPS110
    ) -> models.QuerySet:
        """Get queryset."""
        # TODO fix it (team members case)
        if issubclass(queryset.model, User):
            queryset = queryset.filter(is_active=True, roles__gt=0)

        return queryset

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get user metrics."""
        service = injector.get(IUserMetricsService)
        return service.get_metrics(self, get_fields_from_info(info))

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get user problems."""
        service = injector.get(IUserProblemsService)
        return service.get_problems(self)
