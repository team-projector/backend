import graphene


class IssuesSummaryType(graphene.ObjectType):
    issues_count = graphene.Int()
    time_spent = graphene.Int()
    problems_count = graphene.Int()
