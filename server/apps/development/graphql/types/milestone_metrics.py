import graphene


class MilestoneMetricsType(graphene.ObjectType):
    profit = graphene.Int()
    budget_remains = graphene.Int()
