import graphene


class MilestoneMetricsType(graphene.ObjectType):
    customer_payroll = graphene.Float()
    payroll = graphene.Float()
    budget_remains = graphene.Int()
    profit = graphene.Int()
    time_estimate = graphene.Int()
    time_spent = graphene.Int()
    time_remains = graphene.Int()
    issues_count = graphene.Int()
    issues_opened_count = graphene.Int()
    issues_closed_count = graphene.Int()
    efficiency = graphene.Float()
