import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.types import BitField

from apps.core.graphql.types import BaseModelObjectType
from apps.development.models import TeamMember
from apps.users.graphql.types import UserType


class TeamMemberType(BaseModelObjectType):
    """Team member type."""

    class Meta:
        model = TeamMember

    roles = BitField()
    user = graphene.Field(UserType)

    @classmethod
    def get_queryset(
        cls,
        queryset: QuerySet,
        info,  # noqa: WPS110
    ) -> QuerySet:
        """Get queryset."""
        return queryset.filter(user__is_active=True)
