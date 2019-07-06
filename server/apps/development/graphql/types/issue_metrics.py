import graphene


class IssueMetrics(graphene.ObjectType):
    remains = graphene.Int()
    efficiency = graphene.Float()
    payroll = graphene.Float()
    paid = graphene.Float()
