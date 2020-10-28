import graphene


class ProjectsSummaryType(graphene.ObjectType):
    """Project summary graphene type."""

    count = graphene.Int()
    archived_count = graphene.Int()
    supporting_count = graphene.Int()
    developing_count = graphene.Int()
