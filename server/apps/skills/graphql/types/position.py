import graphene

from apps.core.graphql.types import BaseModelObjectType
from apps.skills.models import Position


class PositionType(BaseModelObjectType):
    """Position type."""

    class Meta:
        model = Position

    title = graphene.String()
