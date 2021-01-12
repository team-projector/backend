import graphene
from jnt_django_graphene_toolbox.types import BaseModelObjectType

from apps.development.models import Label


class LabelType(BaseModelObjectType):
    """Label type."""

    class Meta:
        model = Label
        auth_required = True

    title = graphene.String()
    color = graphene.String()
