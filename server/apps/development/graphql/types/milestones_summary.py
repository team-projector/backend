import graphene
from jnt_django_graphene_toolbox.security.mixins.node import AuthNode


class MilestonesSummaryType(AuthNode, graphene.ObjectType):
    """Milestones summary type."""

    auth_required = True

    count = graphene.Int()
    active_count = graphene.Int()
    closed_count = graphene.Int()
