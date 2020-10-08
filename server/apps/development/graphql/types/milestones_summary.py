import graphene
from jnt_django_graphene_toolbox.security.mixins.node import AuthNode
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated


class MilestonesSummaryType(AuthNode, graphene.ObjectType):
    """Milestones summary type."""

    permission_classes = (AllowAuthenticated,)

    count = graphene.Int()
    active_count = graphene.Int()
    closed_count = graphene.Int()
