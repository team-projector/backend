import graphene

from apps.core.graphql.types import BaseModelObjectType
from apps.development.models import Label


class LabelType(BaseModelObjectType):
    """Label type."""

    class Meta:
        model = Label

    title = graphene.String()
    color = graphene.String()
