import graphene
from jnt_django_graphene_toolbox.security.mixins.node import AuthNode


class MergeRequestsSummaryType(AuthNode, graphene.ObjectType):
    """Merge requests summary type."""

    auth_required = True

    count = graphene.Int()
    opened_count = graphene.Int()
    closed_count = graphene.Int()
    merged_count = graphene.Int()
