import graphene


class IssuesContainerMetricsType(graphene.ObjectType):
    time_estimate = graphene.Int()
    time_spent = graphene.Int()
    time_remains = graphene.Int()
    issues_count = graphene.Int()
    issues_closed_count = graphene.Int()
    issues_opened_count = graphene.Int()
    efficiency = graphene.Float()
    payroll = graphene.Float()
    customer_payroll = graphene.Float()
