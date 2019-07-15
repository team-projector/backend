import graphene


class UserProgressMetricsType(graphene.ObjectType):
    start = graphene.Date()
    end = graphene.Date()
    time_estimate = graphene.Int()
    time_spent = graphene.Int()
    time_remains = graphene.Int()
    issues_count = graphene.Int()
    loading = graphene.Int()
    efficiency = graphene.Float()
    payroll = graphene.Float()
    paid = graphene.Float()
    planned_work_hours = graphene.Int()
