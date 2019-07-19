import graphene


class WorkItemUserMetricsType(graphene.ObjectType):
    opened_count = graphene.Int()
    closed_spent = graphene.Float()
    opened_spent = graphene.Float()
