import graphene


class TeamMetricsType(graphene.ObjectType):
    issues_count = graphene.Int()
    problems_count = graphene.Int()
    issues_opened_count = graphene.Int()
    # remains = graphene.Float()
    # efficiency = graphene.Float()
