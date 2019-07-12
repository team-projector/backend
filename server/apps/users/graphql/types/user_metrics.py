import graphene


class UserMetricsType(graphene.ObjectType):
    payroll_closed = graphene.Float()
    payroll_opened = graphene.Float()
    bonus = graphene.Float()
    penalty = graphene.Float()
    issues_opened_count = graphene.Int()
    issues_closed_spent = graphene.Float()
    issues_opened_spent = graphene.Float()
