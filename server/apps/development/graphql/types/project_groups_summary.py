import graphene


class ProjectGroupsSummaryType(graphene.ObjectType):
    """Project groups summary graphene type."""

    count = graphene.Int()
    archived_count = graphene.Int()
    supporting_count = graphene.Int()
    developing_count = graphene.Int()
