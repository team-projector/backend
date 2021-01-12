import graphene
from jnt_django_graphene_toolbox.types import BaseModelObjectType

from apps.skills.models import Position


class PositionType(BaseModelObjectType):
    """Position type."""

    class Meta:
        model = Position

    title = graphene.String()
