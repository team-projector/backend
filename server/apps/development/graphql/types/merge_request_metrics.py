import graphene


class MergeRequestMetricsType(graphene.ObjectType):
    """Merge request metrics type."""

    remains = graphene.Int()
    efficiency = graphene.Float()
    payroll = graphene.Float()
    paid = graphene.Float()
