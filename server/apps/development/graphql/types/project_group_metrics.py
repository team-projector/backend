import graphene


class ProjectGroupMetricsType(graphene.ObjectType):
    """Project group metrics graphene type."""

    budget = graphene.Float()
    budget_spent = graphene.Float()
    budget_remains = graphene.Float()
    payroll = graphene.Float()
    profit = graphene.Float()
